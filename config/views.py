"""Custom site-wide views (language switcher)."""

from django.conf import settings
from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme


SUPPORTED_LANGS = {code for code, _ in settings.LANGUAGES}
DEFAULT_LANG = settings.LANGUAGE_CODE


def _strip_lang_prefix(path: str) -> str:
    """Remove a leading /xx/ language prefix from a URL path, if present."""
    if not path or not path.startswith('/'):
        return '/'
    parts = path.split('/', 2)
    # parts: ['', 'xx', 'rest...']
    if len(parts) >= 2 and parts[1] in SUPPORTED_LANGS:
        rest = '/' + parts[2] if len(parts) == 3 else '/'
        if not rest.startswith('/'):
            rest = '/' + rest
        return rest
    return path


def set_language(request):
    """Set the language cookie and redirect to the same page in the new language.

    Accepts POST with 'language' and optional 'next'. The 'next' should be the
    full path the user was on (incl. query string). We strip any existing
    language prefix and add the new one (or none, for the default language).
    """
    lang = request.POST.get('language') or request.GET.get('language') or DEFAULT_LANG
    if lang not in SUPPORTED_LANGS:
        lang = DEFAULT_LANG

    next_url = request.POST.get('next') or request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'

    # Only allow internal redirects.
    allowed_hosts = {request.get_host()}
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts=allowed_hosts):
        next_url = '/'

    # Strip query/host parts to get just the path.
    from urllib.parse import urlparse, urlunparse
    parsed = urlparse(next_url)
    path = _strip_lang_prefix(parsed.path or '/')

    # Build the new path with the new language prefix (default lang has no prefix).
    if lang == DEFAULT_LANG:
        new_path = path
    else:
        new_path = f'/{lang}{path}'
        if not new_path.endswith('/') and '?' not in new_path and '#' not in new_path:
            # Keep trailing slash consistent
            pass

    # Re-attach query and fragment
    new_url = urlunparse(('', '', new_path, parsed.params, parsed.query, parsed.fragment))

    response = HttpResponseRedirect(new_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=settings.LANGUAGE_COOKIE_AGE,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response
