from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from .models import User, Tariff, UserSubscription, Payment, Notification


# ─────────────────────────────────────────────
# RO'YXATDAN O'TISH
# ─────────────────────────────────────────────
def register_view(request):
    if request.user.is_authenticated:
        return redirect('house_list')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        phone      = request.POST.get('phone', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        if not all([first_name, last_name, phone, password1, password2]):
            messages.error(request, "Barcha maydonlarni to'ldiring.")
            return render(request, 'users/register.html')

        if password1 != password2:
            messages.error(request, "Parollar mos kelmadi.")
            return render(request, 'users/register.html')

        if len(password1) < 8:
            messages.error(request, "Parol kamida 8 ta belgidan iborat bo'lishi kerak.")
            return render(request, 'users/register.html')

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Bu telefon raqam allaqachon ro'yxatdan o'tgan.")
            return render(request, 'users/register.html')

        user = User.objects.create_user(
            username   = phone,
            phone      = phone,
            first_name = first_name,
            last_name  = last_name,
            password   = password1,
        )
        login(request, user)
        messages.success(request, "Ro'yxatdan muvaffaqiyatli o'tdingiz!")
        return redirect('house_list')

    return render(request, 'users/register.html')


# ─────────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('house_list')

    if request.method == 'POST':
        phone    = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        if not phone or not password:
            messages.error(request, "Telefon va parolni kiriting.")
            return render(request, 'users/login.html')

        user = authenticate(request, username=phone, password=password)

        if user is None:
            messages.error(request, "Telefon raqam yoki parol noto'g'ri.")
            return render(request, 'users/login.html')

        if user.is_blocked:
            messages.error(request, "Sizning hisobingiz bloklangan.")
            return render(request, 'users/login.html')

        login(request, user)
        messages.success(request, f"Xush kelibsiz, {user.first_name}!")
        next_url = request.GET.get('next', 'house_list')
        return redirect(next_url)

    return render(request, 'users/login.html')


# ─────────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────────
def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('house_list')

    logout(request)
    messages.success(request, "Tizimdan chiqdingiz.")
    return redirect('house_list')


# ─────────────────────────────────────────────
# PROFIL
# ─────────────────────────────────────────────
def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/?next=/users/profile/')

    user          = request.user
    subscription  = user.active_subscription
    notifications = user.notifications.filter(is_read=False)[:10]
    payments      = user.payments.all()[:10]
    houses        = user.houses.filter(is_active=True).prefetch_related('images').order_by('-created_at')

    context = {
        'user'         : user,
        'subscription' : subscription,
        'notifications': notifications,
        'payments'     : payments,
        'houses'       : houses,
    }
    return render(request, 'users/profile.html', context)


def my_houses_view(request):
    if not request.user.is_authenticated:
        return redirect('/users/login/?next=/users/my-houses/')

    houses = request.user.houses.filter(is_active=True) \
        .prefetch_related('images').order_by('-created_at')

    return render(request, 'users/my_houses.html', {
        'houses': houses,
        'subscription': request.user.active_subscription,
    })


# ─────────────────────────────────────────────
# PROFIL TAHRIRLASH
# ─────────────────────────────────────────────
def profile_edit_view(request):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/users/profile/edit/")

    user = request.user

    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        card_holder = request.POST.get('card_holder', '').strip()
        card_expiry = request.POST.get('card_expiry', '').strip()
        avatar      = request.FILES.get('avatar')

        if not first_name or not last_name:
            messages.error(request, "Ism va familiyani kiriting.")
            return render(request, 'users/profile_edit.html', {'user': user})

        user.first_name  = first_name
        user.last_name   = last_name
        user.card_number = card_number
        user.card_holder = card_holder
        user.card_expiry = card_expiry

        if avatar:
            user.avatar = avatar

        user.save()
        messages.success(request, "Ma'lumotlar muvaffaqiyatli yangilandi.")
        return redirect('profile')

    return render(request, 'users/profile_edit.html', {'user': user})


# ─────────────────────────────────────────────
# BALANS TO'LDIRISH
# ─────────────────────────────────────────────
def top_up_balance_view(request):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/users/balance/top-up/")

    if request.method == 'POST':
        amount = request.POST.get('amount', '').strip()

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, "Noto'g'ri summa kiritildi.")
            return redirect('profile')

        request.user.balance += amount
        request.user.save(update_fields=['balance'])
        messages.success(request, f"Balansga {amount:,} so'm qo'shildi.")
        return redirect('profile')

    return redirect('profile')


# ─────────────────────────────────────────────
# TARIFLAR SAHIFASI
# ─────────────────────────────────────────────
def tariff_list_view(request):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/users/tariffs/")

    tariffs      = Tariff.objects.filter(is_active=True)
    subscription = request.user.active_subscription

    context = {
        'tariffs'     : tariffs,
        'subscription': subscription,
    }
    return render(request, 'users/tariffs.html', context)


# ─────────────────────────────────────────────
# TARIF SOTIB OLISH
# ─────────────────────────────────────────────
def buy_tariff_view(request, tariff_id):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/users/tariffs/{tariff_id}/buy/")

    tariff = get_object_or_404(Tariff, id=tariff_id, is_active=True)
    user   = request.user

    if request.method == 'POST':

        if user.balance < tariff.price:
            messages.error(
                request,
                f"Balansda mablag' yetarli emas. "
                f"Kerakli summa: {tariff.price:,.0f} so'm. "
                f"Sizning balansingiz: {user.balance:,.0f} so'm."
            )
            return render(request, 'users/buy_tariff.html', {'tariff': tariff, 'user': user})

        # Avvalgi aktiv obunani o'chirish
        user.subscriptions.filter(is_active=True).update(is_active=False)

        # Yangi obuna yaratish
        subscription = UserSubscription.objects.create(
            user   = user,
            tariff = tariff,
        )

        # To'lov yaratish
        card_masked = '**** **** **** ----'
        if user.card_number and len(user.card_number) >= 4:
            card_masked = '**** **** **** ' + user.card_number[-4:]

        Payment.objects.create(
            user               = user,
            tariff             = tariff,
            subscription       = subscription,
            amount             = tariff.price,
            card_number_masked = card_masked,
            status             = Payment.Status.SUCCESS,
        )

        # Balansdan yechish
        user.balance -= tariff.price
        user.save(update_fields=['balance'])

        # Bildirishnoma
        Notification.objects.create(
            user    = user,
            type    = Notification.Type.GENERAL,
            title   = "Tarif faollashtirildi",
            message = (
                f"{tariff.name} tarifi muvaffaqiyatli faollashtirildi. "
                f"Muddati: {subscription.end_date.strftime('%d.%m.%Y')} gacha."
            ),
        )

        messages.success(
            request,
            f"{tariff.name} muvaffaqiyatli sotib olindi! "
            f"Muddati: {subscription.end_date.strftime('%d.%m.%Y')} gacha."
        )
        return redirect('profile')

    context = {
        'tariff': tariff,
        'user'  : user,
    }
    return render(request, 'users/buy_tariff.html', context)


# ─────────────────────────────────────────────
# WISHLIST
# ─────────────────────────────────────────────
def wishlist_view(request):
    if not request.user.is_authenticated:
        return redirect(f"/users/login/?next=/users/wishlist/")

    wishlist = request.user.wishlist.select_related('house').all()
    context  = {'wishlist': wishlist}
    return render(request, 'users/wishlist.html', context)


# ─────────────────────────────────────────────
# BILDIRISHNOMALARNI O'QILGAN QILISH
# ─────────────────────────────────────────────
def mark_notifications_read(request):
    if not request.user.is_authenticated:
        return redirect('login')

    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('profile')