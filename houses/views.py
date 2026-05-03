from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, F
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext as _

from .models import (
    Comment,
    District,
    House,
    HouseImage,
    HouseRating,
    Region,
    Report,
    Wishlist,
)


def _login_redirect(request):
    """Return a redirect to the login page, preserving the current language and 'next' URL."""
    return redirect(f"{reverse('login')}?next={request.get_full_path()}")


def house_list(request):
    houses = (
        House.objects.filter(is_active=True)
        .prefetch_related('images')
        .select_related('owner', 'region', 'district')
        .order_by('-created_at')
    )

    region_id = request.GET.get('region')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    q         = request.GET.get('q')
    sort      = request.GET.get('sort')

    if region_id:
        houses = houses.filter(region_id=region_id)
    if min_price:
        houses = houses.filter(price_usd__gte=min_price)
    if max_price:
        houses = houses.filter(price_usd__lte=max_price)
    if q:
        houses = houses.filter(full_address__icontains=q)
    if sort == 'cheap':
        houses = houses.order_by('price_usd')
    elif sort == 'expensive':
        houses = houses.order_by('-price_usd')
    elif sort == 'top':
        houses = houses.annotate(avg_r=Avg('ratings__score')).order_by('-avg_r')

    total_count = houses.count()
    paginator = Paginator(houses, 12)
    page_obj  = paginator.get_page(request.GET.get('page'))

    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = list(
            request.user.wishlist.values_list('house_id', flat=True)
        )
    user_wishlist = [h for h in page_obj.object_list if h.pk in user_wishlist_ids]

    return render(request, 'houses/house_list.html', {
        'houses'        : page_obj.object_list,
        'page_obj'      : page_obj,
        'total_count'   : total_count,
        'regions'       : Region.objects.all(),
        'user_wishlist' : user_wishlist,
    })


def get_districts(request):
    region_id = request.GET.get('region_id')
    qs = District.objects.filter(region_id=region_id)
    return JsonResponse({
        'districts': [{'id': d.id, 'name': d.display_name} for d in qs],
    })


def house_detail(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house    = get_object_or_404(House, pk=pk, is_active=True)
    images   = house.images.all()
    comments = house.comments.select_related('user').all()
    similar  = (
        House.objects.filter(district=house.district, is_active=True)
        .exclude(pk=pk)
        .prefetch_related('images')[:4]
    )

    if house.owner != request.user:
        House.objects.filter(pk=house.pk).update(view_count=F('view_count') + 1)
        house.refresh_from_db(fields=['view_count'])

    user_rating = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_rating = HouseRating.objects.filter(house=house, user=request.user).first()
        in_wishlist = Wishlist.objects.filter(house=house, user=request.user).exists()

    avg_rating = house.ratings.aggregate(avg=Avg('score'))['avg'] or 0

    return render(request, 'houses/house_detail.html', {
        'house'      : house,
        'images'     : images,
        'comments'   : comments,
        'similar'    : similar,
        'user_rating': user_rating,
        'avg_rating' : round(avg_rating, 1),
        'in_wishlist': in_wishlist,
        'has_sub'    : request.user.has_active_subscription,
    })


def house_add(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    if not request.user.has_active_subscription:
        messages.error(request, _("Uy qo'shish uchun avval tarif sotib oling."))
        return redirect('tariff_list')

    regions   = Region.objects.all()
    districts = District.objects.all()

    if request.method == 'POST':
        region_id    = request.POST.get('region')
        district_id  = request.POST.get('district')
        street       = request.POST.get('street', '').strip()
        full_address = request.POST.get('full_address', '').strip()
        price_usd    = request.POST.get('price_usd', '').strip()
        description  = request.POST.get('description', '').strip()
        latitude     = request.POST.get('latitude', '').strip().replace(',', '.')
        longitude    = request.POST.get('longitude', '').strip().replace(',', '.')
        images       = request.FILES.getlist('images')

        ctx = {'regions': regions, 'districts': districts}

        if not all([region_id, district_id, street, full_address, price_usd, description]):
            messages.error(request, _("Barcha majburiy maydonlarni to'ldiring."))
            return render(request, 'houses/house_add.html', ctx)

        if len(images) < 1:
            messages.error(request, _("Kamida 1 ta rasm yuklang."))
            return render(request, 'houses/house_add.html', ctx)

        if len(images) > 10:
            messages.error(request, _("Ko'pi bilan 10 ta rasm yuklash mumkin."))
            return render(request, 'houses/house_add.html', ctx)

        try:
            price_usd = float(price_usd)
            if price_usd <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, _("Narxni to'g'ri kiriting."))
            return render(request, 'houses/house_add.html', ctx)

        region   = get_object_or_404(Region, pk=region_id)
        district = get_object_or_404(District, pk=district_id)

        house = House.objects.create(
            owner        = request.user,
            region       = region,
            district     = district,
            street       = street,
            full_address = full_address,
            price_usd    = price_usd,
            description  = description,
            latitude     = latitude or None,
            longitude    = longitude or None,
        )

        for i, image in enumerate(images):
            HouseImage.objects.create(
                house   = house,
                image   = image,
                is_main = (i == 0),
                order   = i,
            )

        messages.success(request, _("Uy muvaffaqiyatli qo'shildi!"))
        return redirect('house_detail', pk=house.pk)

    return render(request, 'houses/house_add.html', {
        'regions'  : regions,
        'districts': districts,
    })


def house_edit(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk, is_active=True)

    if house.owner != request.user:
        messages.error(request, _("Siz bu uyni tahrirlash huquqiga ega emassiz."))
        return redirect('house_detail', pk=pk)

    if not request.user.has_active_subscription:
        messages.error(request, _("Uy tahrirlash uchun aktiv tarif kerak."))
        return redirect('tariff_list')

    regions   = Region.objects.all()
    districts = District.objects.filter(region=house.region)

    if request.method == 'POST':
        region_id    = request.POST.get('region')
        district_id  = request.POST.get('district')
        street       = request.POST.get('street', '').strip()
        full_address = request.POST.get('full_address', '').strip()
        price_usd    = request.POST.get('price_usd', '').strip()
        description  = request.POST.get('description', '').strip()
        latitude     = request.POST.get('latitude', '').strip().replace(',', '.')
        longitude    = request.POST.get('longitude', '').strip().replace(',', '.')
        is_rented    = request.POST.get('is_rented') == 'on'
        new_images   = request.FILES.getlist('images')

        ctx = {'house': house, 'regions': regions, 'districts': districts}

        if not all([region_id, district_id, street, full_address, price_usd, description]):
            messages.error(request, _("Barcha majburiy maydonlarni to'ldiring."))
            return render(request, 'houses/house_edit.html', ctx)

        try:
            price_usd = float(price_usd)
            if price_usd <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, _("Narxni to'g'ri kiriting."))
            return render(request, 'houses/house_edit.html', ctx)

        house.region       = get_object_or_404(Region, pk=region_id)
        house.district     = get_object_or_404(District, pk=district_id)
        house.street       = street
        house.full_address = full_address
        house.price_usd    = price_usd
        house.description  = description
        house.latitude     = latitude or None
        house.longitude    = longitude or None
        house.is_rented    = is_rented
        house.save()

        if new_images:
            existing_count = house.images.count()
            if existing_count + len(new_images) > 10:
                messages.error(request, _("Rasmlar soni 10 tadan oshib ketadi."))
                return render(request, 'houses/house_edit.html', ctx)
            for i, image in enumerate(new_images):
                HouseImage.objects.create(
                    house = house,
                    image = image,
                    order = existing_count + i,
                )

        messages.success(request, _("Uy ma'lumotlari yangilandi."))
        return redirect('house_detail', pk=house.pk)

    return render(request, 'houses/house_edit.html', {
        'house'    : house,
        'regions'  : regions,
        'districts': districts,
    })


def house_delete(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk)

    if house.owner != request.user:
        messages.error(request, _("Siz bu uyni o'chirish huquqiga ega emassiz."))
        return redirect('house_detail', pk=pk)

    if request.method == 'POST':
        house.delete()
        messages.success(request, _("Uy o'chirildi."))
        return redirect('profile')

    return render(request, 'houses/house_delete.html', {'house': house})


def call_view(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk, is_active=True)

    if not request.user.has_active_subscription:
        return JsonResponse({
            'success' : False,
            'message' : _("Telefon raqamni ko'rish uchun premium tarif sotib oling."),
            'redirect': reverse('tariff_list'),
        })

    return JsonResponse({
        'success': True,
        'phone'  : house.owner.phone,
        'name'   : house.owner.get_full_name(),
    })


def report_view(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk, is_active=True)

    if house.owner == request.user:
        messages.error(request, _("O'z uyingizni report qila olmaysiz."))
        return redirect('house_detail', pk=pk)

    if request.method == 'POST':
        if Report.objects.filter(reporter=request.user, house=house).exists():
            messages.warning(request, _("Siz bu uy uchun allaqachon shikoyat yuborgansiz."))
            return redirect('house_detail', pk=pk)

        Report.objects.create(
            reporter      = request.user,
            reported_user = house.owner,
            house         = house,
        )
        messages.success(request, _("Shikoyatingiz qabul qilindi. Rahmat!"))
        return redirect('house_detail', pk=pk)

    return render(request, 'houses/report.html', {'house': house})


def toggle_wishlist(request, pk):
    if not request.user.is_authenticated:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'redirect': reverse('login')}, status=401)
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk, is_active=True)
    item  = Wishlist.objects.filter(user=request.user, house=house).first()

    if item:
        item.delete()
        saved = False
        msg   = _("Uy saqlanganlardan olib tashlandi.")
    else:
        Wishlist.objects.create(user=request.user, house=house)
        saved = True
        msg   = _("Uy saqlanganlar ro'yxatiga qo'shildi.")

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'saved': saved, 'message': str(msg)})

    messages.success(request, msg)
    return redirect('house_detail', pk=pk)


def add_comment(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk, is_active=True)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()

        if not text:
            messages.error(request, _("Izoh matni bo'sh bo'lishi mumkin emas."))
            return redirect('house_detail', pk=pk)

        if len(text) > 1000:
            messages.error(request, _("Izoh 1000 ta belgidan oshmasligi kerak."))
            return redirect('house_detail', pk=pk)

        Comment.objects.create(house=house, user=request.user, text=text)
        messages.success(request, _("Izohingiz qo'shildi."))

    return redirect('house_detail', pk=pk)


def add_rating(request, pk):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    house = get_object_or_404(House, pk=pk, is_active=True)

    if house.owner == request.user:
        messages.error(request, _("O'z uyingizga baho bera olmaysiz."))
        return redirect('house_detail', pk=pk)

    if request.method == 'POST':
        try:
            score = int(request.POST.get('score'))
            if score < 1 or score > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, _("Baho 1 dan 5 gacha bo'lishi kerak."))
            return redirect('house_detail', pk=pk)

        HouseRating.objects.update_or_create(
            house=house, user=request.user,
            defaults={'score': score},
        )
        messages.success(request, _("Bahoyingiz qabul qilindi."))

    return redirect('house_detail', pk=pk)


def delete_image(request, image_id):
    if not request.user.is_authenticated:
        return redirect('login')

    image = get_object_or_404(HouseImage, pk=image_id)

    if image.house.owner != request.user:
        messages.error(request, _("Ruxsat yo'q."))
        return redirect('house_detail', pk=image.house.pk)

    if request.method == 'POST':
        house_pk = image.house.pk
        image.delete()
        messages.success(request, _("Rasm o'chirildi."))
        return redirect('house_edit', pk=house_pk)

    return redirect('house_edit', pk=image.house.pk)
