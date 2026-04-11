from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Avg
from .models import House, HouseImage, HouseRating, Comment, Wishlist, Report, Region, District





def house_list(request):
    houses = House.objects.filter(is_active=True)\
        .prefetch_related('images')\
        .select_related('owner', 'region', 'district')\
        .order_by('-created_at')

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

    regions = Region.objects.all()

    samarqand_houses = House.objects.filter(
        is_active=True,
        region__name__icontains='Samarqand'
    ).prefetch_related('images')\
     .select_related('owner', 'region', 'district')\
     .order_by('-created_at')[:6]

    return render(request, 'houses/house_list.html', {
        'houses'           : houses,
        'regions'          : regions,
        'samarqand_houses' : samarqand_houses,
    })


def get_districts(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    from django.http import JsonResponse
    return JsonResponse({'districts': list(districts)})


def house_detail(request, pk):
    # Login tekshiruvi
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/")

    house    = get_object_or_404(House, pk=pk, is_active=True)
    images   = house.images.all()
    comments = house.comments.select_related('user').all()
    similar  = House.objects.filter(
        district=house.district,
        is_active=True
    ).exclude(pk=pk).prefetch_related('images')[:4]


    user_rating = None
    in_wishlist = False
    if request.user.is_authenticated:
        user_rating = HouseRating.objects.filter(house=house, user=request.user).first()
        in_wishlist = Wishlist.objects.filter(house=house, user=request.user).exists()


    avg_rating = house.ratings.aggregate(avg=Avg('score'))['avg'] or 0

    context = {
        'house'      : house,
        'images'     : images,
        'comments'   : comments,
        'similar'    : similar,
        'user_rating': user_rating,
        'avg_rating' : round(avg_rating, 1),
        'in_wishlist': in_wishlist,
        'has_sub'    : request.user.has_active_subscription,
    }
    return render(request, 'houses/house_detail.html', context)



def house_add(request):
    if not request.user.is_authenticated:
        return redirect("/users/login/?next=/houses/add/")


    if not request.user.has_active_subscription:
        messages.error(request, "Uy qo'shish uchun avval tarif sotib oling.")
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
        latitude = request.POST.get('latitude', '').strip().replace(',', '.')
        longitude = request.POST.get('longitude', '').strip().replace(',', '.')
        images       = request.FILES.getlist('images')


        if not all([region_id, district_id, street, full_address, price_usd, description]):
            messages.error(request, "Barcha majburiy maydonlarni to'ldiring.")
            return render(request, 'houses/house_add.html', {
                'regions': regions, 'districts': districts
            })

        if len(images) < 1:
            messages.error(request, "Kamida 1 ta rasm yuklang.")
            return render(request, 'houses/house_add.html', {
                'regions': regions, 'districts': districts
            })

        if len(images) > 10:
            messages.error(request, "Ko'pi bilan 10 ta rasm yuklash mumkin.")
            return render(request, 'houses/house_add.html', {
                'regions': regions, 'districts': districts
            })

        try:
            price_usd = float(price_usd)
            if price_usd <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Narxni to'g'ri kiriting.")
            return render(request, 'houses/house_add.html', {
                'regions': regions, 'districts': districts
            })

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
            latitude     = latitude if latitude else None,
            longitude    = longitude if longitude else None,
        )


        for i, image in enumerate(images):
            HouseImage.objects.create(
                house   = house,
                image   = image,
                is_main = (i == 0),  # Birinchi rasm — asosiy
                order   = i,
            )

        messages.success(request, "Uy muvaffaqiyatli qo'shildi!")
        return redirect('house_detail', pk=house.pk)

    context = {
        'regions'  : regions,
        'districts': districts,
    }
    return render(request, 'houses/house_add.html', context)



def house_edit(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/edit/")

    house = get_object_or_404(House, pk=pk, is_active=True)


    if house.owner != request.user:
        messages.error(request, "Siz bu uyni tahrirlash huquqiga ega emassiz.")
        return redirect('house_detail', pk=pk)

    if not request.user.has_active_subscription:
        messages.error(request, "Uy tahrirlash uchun aktiv tarif kerak.")
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
        latitude = request.POST.get('latitude', '').strip().replace(',', '.')
        longitude = request.POST.get('longitude', '').strip().replace(',', '.')
        new_images   = request.FILES.getlist('images')

        if not all([region_id, district_id, street, full_address, price_usd, description]):
            messages.error(request, "Barcha majburiy maydonlarni to'ldiring.")
            return render(request, 'houses/house_edit.html', {
                'house': house, 'regions': regions, 'districts': districts
            })

        try:
            price_usd = float(price_usd)
            if price_usd <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Narxni to'g'ri kiriting.")
            return render(request, 'houses/house_edit.html', {
                'house': house, 'regions': regions, 'districts': districts
            })

        house.region       = get_object_or_404(Region, pk=region_id)
        house.district     = get_object_or_404(District, pk=district_id)
        house.street       = street
        house.full_address = full_address
        house.price_usd    = price_usd
        house.description  = description
        house.latitude     = latitude if latitude else None
        house.longitude    = longitude if longitude else None
        house.save()


        if new_images:
            existing_count = house.images.count()
            if existing_count + len(new_images) > 10:
                messages.error(request, "Rasmlar soni 10 tadan oshib ketadi.")
                return render(request, 'houses/house_edit.html', {
                    'house': house, 'regions': regions, 'districts': districts
                })
            for i, image in enumerate(new_images):
                HouseImage.objects.create(
                    house = house,
                    image = image,
                    order = existing_count + i,
                )

        messages.success(request, "Uy ma'lumotlari yangilandi.")
        return redirect('house_detail', pk=house.pk)

    context = {
        'house'    : house,
        'regions'  : regions,
        'districts': districts,
    }
    return render(request, 'houses/house_edit.html', context)



def house_delete(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/delete/")

    house = get_object_or_404(House, pk=pk)


    if house.owner != request.user:
        messages.error(request, "Siz bu uyni o'chirish huquqiga ega emassiz.")
        return redirect('house_detail', pk=pk)

    if request.method == 'POST':
        house.delete()
        messages.success(request, "Uy o'chirildi.")
        return redirect('profile')

    return render(request, 'houses/house_delete.html', {'house': house})



def call_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/")

    house = get_object_or_404(House, pk=pk, is_active=True)


    if not request.user.has_active_subscription:
        from django.http import JsonResponse
        return JsonResponse({
            'success': False,
            'message': "Telefon raqamni ko'rish uchun premium tarif sotib oling.",
            'redirect': '/users/tariffs/'
        })

    from django.http import JsonResponse
    return JsonResponse({
        'success': True,
        'phone'  : house.owner.phone,
        'name'   : house.owner.get_full_name(),
    })



def report_view(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/")

    house = get_object_or_404(House, pk=pk, is_active=True)


    if house.owner == request.user:
        messages.error(request, "O'z uyingizni report qila olmaysiz.")
        return redirect('house_detail', pk=pk)

    if request.method == 'POST':

        already = Report.objects.filter(reporter=request.user, house=house).exists()
        if already:
            messages.warning(request, "Siz bu uy uchun allaqachon shikoyat yuborgansiz.")
            return redirect('house_detail', pk=pk)

        Report.objects.create(
            reporter      = request.user,
            reported_user = house.owner,
            house         = house,
        )
        messages.success(request, "Shikoyatingiz qabul qilindi. Rahmat!")
        return redirect('house_detail', pk=pk)

    return render(request, 'houses/report.html', {'house': house})



def toggle_wishlist(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/")

    house = get_object_or_404(House, pk=pk, is_active=True)

    wishlist_item = Wishlist.objects.filter(user=request.user, house=house).first()

    if wishlist_item:
        wishlist_item.delete()
        messages.success(request, "Uy saqlanganlardan olib tashlandi.")
    else:
        Wishlist.objects.create(user=request.user, house=house)
        messages.success(request, "Uy saqlanganlar ro'yxatiga qo'shildi.")

    return redirect('house_detail', pk=pk)



def add_comment(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/")

    house = get_object_or_404(House, pk=pk, is_active=True)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()

        if not text:
            messages.error(request, "Izoh matni bo'sh bo'lishi mumkin emas.")
            return redirect('house_detail', pk=pk)

        if len(text) > 1000:
            messages.error(request, "Izoh 1000 ta belgidan oshmasligi kerak.")
            return redirect('house_detail', pk=pk)

        Comment.objects.create(
            house = house,
            user  = request.user,
            text  = text,
        )
        messages.success(request, "Izohingiz qo'shildi.")

    return redirect('house_detail', pk=pk)


def add_rating(request, pk):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/houses/{pk}/")

    house = get_object_or_404(House, pk=pk, is_active=True)


    if house.owner == request.user:
        messages.error(request, "O'z uyingizga baho bera olmaysiz.")
        return redirect('house_detail', pk=pk)

    if request.method == 'POST':
        score = request.POST.get('score')

        try:
            score = int(score)
            if score < 1 or score > 5:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Baho 1 dan 5 gacha bo'lishi kerak.")
            return redirect('house_detail', pk=pk)


        HouseRating.objects.update_or_create(
            house = house,
            user  = request.user,
            defaults={'score': score},
        )
        messages.success(request, "Bahoyingiz qabul qilindi.")

    return redirect('house_detail', pk=pk)



def delete_image(request, image_id):
    if not request.user.is_authenticated:
        return redirect('/users/login/')

    image = get_object_or_404(HouseImage, pk=image_id)


    if image.house.owner != request.user:
        messages.error(request, "Ruxsat yo'q.")
        return redirect('house_detail', pk=image.house.pk)

    if request.method == 'POST':
        house_pk = image.house.pk
        image.delete()
        messages.success(request, "Rasm o'chirildi.")
        return redirect('house_edit', pk=house_pk)

    return redirect('house_edit', pk=image.house.pk)