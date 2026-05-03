

"""Lightweight JSON API for the future mobile app.

Uses plain JsonResponse (no DRF dependency). Read-only endpoints first;
write endpoints can be added when the mobile client lands.
"""
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST

from .models import District, House, Region, Wishlist


def _serialize_house(house, request, detail=False):
    """Convert a House instance to a JSON-serializable dict."""
    main_img = house.main_image
    data = {
        'id'           : house.pk,
        'price_usd'    : str(house.price_usd),
        'full_address' : house.full_address,
        'street'       : house.street,
        'is_rented'    : house.is_rented,
        'view_count'   : house.view_count,
        'created_at'   : house.created_at.isoformat(),
        'region'       : {'id': house.region_id, 'name': house.region.display_name},
        'district'     : {'id': house.district_id, 'name': house.district.display_name},
        'main_image'   : request.build_absolute_uri(main_img.image.url) if main_img else None,
        'rating'       : float(house.average_rating),
    }
    if detail:
        data.update({
            'description' : house.description,
            'latitude'    : str(house.latitude) if house.latitude else None,
            'longitude'   : str(house.longitude) if house.longitude else None,
            'images'      : [
                request.build_absolute_uri(img.image.url) for img in house.images.all()
            ],
            'owner': {
                'id'        : house.owner_id,
                'full_name' : house.owner.get_full_name(),
                'avatar'    : (request.build_absolute_uri(house.owner.avatar.url)
                               if house.owner.avatar else None),
            },
            'comments_count': house.comments.count(),
        })
    return data


@require_http_methods(['GET'])
def api_houses(request):
    qs = (House.objects.filter(is_active=True)
          .select_related('owner', 'region', 'district')
          .prefetch_related('images')
          .order_by('-created_at'))

    region_id = request.GET.get('region')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    q         = request.GET.get('q')
    sort      = request.GET.get('sort')

    if region_id:    qs = qs.filter(region_id=region_id)
    if min_price:    qs = qs.filter(price_usd__gte=min_price)
    if max_price:    qs = qs.filter(price_usd__lte=max_price)
    if q:            qs = qs.filter(full_address__icontains=q)
    if sort == 'cheap':     qs = qs.order_by('price_usd')
    elif sort == 'expensive': qs = qs.order_by('-price_usd')
    elif sort == 'top':       qs = qs.annotate(avg_r=Avg('ratings__score')).order_by('-avg_r')

    page = int(request.GET.get('page', 1))
    paginator = Paginator(qs, 20)
    page_obj = paginator.get_page(page)

    return JsonResponse({
        'count'    : paginator.count,
        'page'     : page_obj.number,
        'pages'    : paginator.num_pages,
        'has_next' : page_obj.has_next(),
        'results'  : [_serialize_house(h, request) for h in page_obj.object_list],
    })


@require_http_methods(['GET'])
def api_house_detail(request, pk):
    house = get_object_or_404(
        House.objects.select_related('owner', 'region', 'district').prefetch_related('images'),
        pk=pk, is_active=True,
    )
    return JsonResponse(_serialize_house(house, request, detail=True))


@require_http_methods(['GET'])
def api_regions(request):
    return JsonResponse({
        'results': [{'id': r.id, 'name': r.display_name} for r in Region.objects.all()],
    })


@require_http_methods(['GET'])
def api_districts(request):
    region_id = request.GET.get('region_id')
    qs = District.objects.all()
    if region_id:
        qs = qs.filter(region_id=region_id)
    return JsonResponse({
        'results': [
            {'id': d.id, 'name': d.display_name, 'region_id': d.region_id}
            for d in qs
        ],
    })


@require_POST
@csrf_exempt
def api_toggle_wishlist(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'authentication_required'}, status=401)

    house = get_object_or_404(House, pk=pk, is_active=True)
    item = Wishlist.objects.filter(user=request.user, house=house).first()
    if item:
        item.delete()
        return JsonResponse({'saved': False})
    Wishlist.objects.create(user=request.user, house=house)
    return JsonResponse({'saved': True})


@require_http_methods(['GET'])
def api_me(request):
    if not request.user.is_authenticated:
        return JsonResponse({'authenticated': False})
    u = request.user
    sub = u.active_subscription
    return JsonResponse({
        'authenticated': True,
        'id'           : u.id,
        'phone'        : u.phone,
        'first_name'   : u.first_name,
        'last_name'    : u.last_name,
        'avatar'       : request.build_absolute_uri(u.avatar.url) if u.avatar else None,
        'balance'      : str(u.balance),
        'subscription' : {
            'tariff'   : sub.tariff.name,
            'end_date' : sub.end_date.isoformat(),
            'days_left': sub.days_left,
        } if sub else None,
        'unread_notifications': u.notifications.filter(is_read=False).count(),
    })
