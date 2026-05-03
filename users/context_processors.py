def user_extras(request):
    """Inject unread notification count for the navbar bell."""
    if not request.user.is_authenticated:
        return {'unread_notifications_count': 0}
    return {
        'unread_notifications_count': request.user.notifications.filter(is_read=False).count(),
    }
