from datetime import timedelta

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext as _

from houses.models import House, Report

from .models import Notification, Payment, Tariff, User, UserSubscription


def _login_redirect(request):
    """Redirect to login while keeping the active language and the original path."""
    return redirect(f"{reverse('login')}?next={request.get_full_path()}")


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
            messages.error(request, _("Barcha maydonlarni to'ldiring."))
            return render(request, 'users/register.html')

        if password1 != password2:
            messages.error(request, _("Parollar mos kelmadi."))
            return render(request, 'users/register.html')

        if len(password1) < 8:
            messages.error(request, _("Parol kamida 8 ta belgidan iborat bo'lishi kerak."))
            return render(request, 'users/register.html')

        if User.objects.filter(phone=phone).exists():
            messages.error(request, _("Bu telefon raqam allaqachon ro'yxatdan o'tgan."))
            return render(request, 'users/register.html')

        user = User.objects.create_user(
            username   = phone,
            phone      = phone,
            first_name = first_name,
            last_name  = last_name,
            password   = password1,
        )
        login(request, user)
        messages.success(request, _("Ro'yxatdan muvaffaqiyatli o'tdingiz!"))
        return redirect('house_list')

    return render(request, 'users/register.html')


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        return redirect('house_list')

    if request.method == 'POST':
        phone    = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')

        if not phone or not password:
            messages.error(request, _("Telefon va parolni kiriting."))
            return render(request, 'users/login.html')

        user = authenticate(request, username=phone, password=password)

        if user is not None:
            if user.is_blocked:
                messages.error(request, _("Sizning hisobingiz ko'p sonli shikoyatlar tufayli bloklangan."))
                return render(request, 'users/login.html')

            login(request, user)
            messages.success(request, _("Xush kelibsiz, %(name)s!") % {'name': user.first_name})

            if user.is_staff:
                return redirect('admin_dashboard')

            next_url = request.POST.get('next') or request.GET.get('next') or ''
            # Only follow safe internal next URLs; otherwise go to default home.
            if next_url.startswith('/'):
                return redirect(next_url)
            return redirect('house_list')

        messages.error(request, _("Telefon raqam yoki parol noto'g'ri."))
        return render(request, 'users/login.html')

    return render(request, 'users/login.html')


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect('house_list')

    logout(request)
    messages.success(request, _("Tizimdan chiqdingiz."))
    return redirect('house_list')


def profile_view(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    user = request.user
    return render(request, 'users/profile.html', {
        'user'         : user,
        'subscription' : user.active_subscription,
        'notifications': user.notifications.filter(is_read=False)[:10],
        'payments'     : user.payments.all()[:10],
        'houses'       : user.houses.filter(is_active=True).prefetch_related('images').order_by('-created_at'),
    })


def my_houses_view(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    houses = (
        request.user.houses.filter(is_active=True)
        .prefetch_related('images').order_by('-created_at')
    )
    return render(request, 'users/my_houses.html', {
        'houses'      : houses,
        'subscription': request.user.active_subscription,
    })


def profile_edit_view(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    user = request.user

    if request.method == 'POST':
        first_name  = request.POST.get('first_name', '').strip()
        last_name   = request.POST.get('last_name', '').strip()
        card_number = request.POST.get('card_number', '').strip()
        card_holder = request.POST.get('card_holder', '').strip()
        card_expiry = request.POST.get('card_expiry', '').strip()
        avatar      = request.FILES.get('avatar')

        if not first_name or not last_name:
            messages.error(request, _("Ism va familiyani kiriting."))
            return render(request, 'users/profile_edit.html', {'user': user})

        user.first_name  = first_name
        user.last_name   = last_name
        user.card_number = card_number
        user.card_holder = card_holder
        user.card_expiry = card_expiry

        if avatar:
            user.avatar = avatar

        user.save()
        messages.success(request, _("Ma'lumotlar muvaffaqiyatli yangilandi."))
        return redirect('profile')

    return render(request, 'users/profile_edit.html', {'user': user})


def top_up_balance_view(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', '').strip())
            if amount <= 0:
                raise ValueError
        except ValueError:
            messages.error(request, _("Noto'g'ri summa kiritildi."))
            return redirect('profile')

        request.user.balance += amount
        request.user.save(update_fields=['balance'])
        messages.success(request, _("Balansga %(amount)s so'm qo'shildi.") % {'amount': f'{amount:,}'})
        return redirect('profile')

    return redirect('profile')


def tariff_list_view(request):
    return render(request, 'users/tariffs.html', {
        'tariffs'     : Tariff.objects.filter(is_active=True),
        'subscription': request.user.active_subscription if request.user.is_authenticated else None,
    })


def buy_tariff_view(request, tariff_id):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    tariff = get_object_or_404(Tariff, id=tariff_id, is_active=True)
    user   = request.user

    if request.method == 'POST':
        if user.balance < tariff.price:
            messages.error(request, _(
                "Balansda mablag' yetarli emas. "
                "Kerakli summa: %(need)s so'm. Sizning balansingiz: %(have)s so'm."
            ) % {
                'need': f'{tariff.price:,.0f}',
                'have': f'{user.balance:,.0f}',
            })
            return render(request, 'users/buy_tariff.html', {'tariff': tariff, 'user': user})

        user.subscriptions.filter(is_active=True).update(is_active=False)

        subscription = UserSubscription.objects.create(user=user, tariff=tariff)

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

        user.balance -= tariff.price
        user.save(update_fields=['balance'])

        Notification.objects.create(
            user    = user,
            type    = Notification.Type.GENERAL,
            title   = _("Tarif faollashtirildi"),
            message = _("%(name)s tarifi muvaffaqiyatli faollashtirildi. Muddati: %(date)s gacha.") % {
                'name': tariff.name,
                'date': subscription.end_date.strftime('%d.%m.%Y'),
            },
        )

        messages.success(request, _("%(name)s muvaffaqiyatli sotib olindi! Muddati: %(date)s gacha.") % {
            'name': tariff.name,
            'date': subscription.end_date.strftime('%d.%m.%Y'),
        })
        return redirect('profile')

    return render(request, 'users/buy_tariff.html', {'tariff': tariff, 'user': user})


def wishlist_view(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    wishlist = request.user.wishlist.select_related('house').all()
    return render(request, 'users/wishlist.html', {'wishlist': wishlist})


def mark_notifications_read(request):
    if not request.user.is_authenticated:
        return redirect('login')

    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER') or 'notifications')


def notifications_view(request):
    if not request.user.is_authenticated:
        return _login_redirect(request)

    notifications = request.user.notifications.all()[:50]
    unread_count = request.user.notifications.filter(is_read=False).count()
    return render(request, 'users/notifications.html', {
        'notifications': notifications,
        'unread_count' : unread_count,
    })


@staff_member_required
def admin_dashboard(request):
    today     = timezone.now()
    week_ago  = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    total_users         = User.objects.count()
    total_houses        = House.objects.filter(is_active=True).count()
    total_reports       = Report.objects.count()
    total_payments      = Payment.objects.filter(status=Payment.Status.SUCCESS).count()
    blocked_users_count = User.objects.filter(is_blocked=True).count()
    new_users_week      = User.objects.filter(date_joined__gte=week_ago).count()
    new_houses_week     = House.objects.filter(created_at__gte=week_ago).count()

    active_subscribers = (
        UserSubscription.objects
        .filter(is_active=True, end_date__gte=today)
        .values('user').distinct().count()
    )

    weekly_income = Payment.objects.filter(
        status=Payment.Status.SUCCESS, created_at__gte=week_ago,
    ).aggregate(total=Sum('amount'))['total'] or 0

    monthly_income = Payment.objects.filter(
        status=Payment.Status.SUCCESS, created_at__gte=month_ago,
    ).aggregate(total=Sum('amount'))['total'] or 0

    total_income = Payment.objects.filter(
        status=Payment.Status.SUCCESS,
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Last 7 days payment chart data
    chart_labels = []
    chart_income = []
    chart_users  = []
    chart_houses = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end   = day_start + timedelta(days=1)
        chart_labels.append(day_start.strftime('%d.%m'))
        chart_income.append(int(
            Payment.objects.filter(
                status=Payment.Status.SUCCESS,
                created_at__gte=day_start, created_at__lt=day_end,
            ).aggregate(t=Sum('amount'))['t'] or 0
        ))
        chart_users.append(
            User.objects.filter(date_joined__gte=day_start, date_joined__lt=day_end).count()
        )
        chart_houses.append(
            House.objects.filter(created_at__gte=day_start, created_at__lt=day_end).count()
        )

    reported_users = (
        User.objects.annotate(reports_count_attr=Count('received_reports'))
        .filter(reports_count_attr__gt=0).order_by('-reports_count_attr')[:5]
    )

    latest_payments = (
        Payment.objects.filter(status=Payment.Status.SUCCESS)
        .select_related('user', 'tariff').order_by('-created_at')[:8]
    )

    latest_houses = (
        House.objects.filter(is_active=True)
        .select_related('owner', 'region', 'district')
        .prefetch_related('images')
        .order_by('-created_at')[:6]
    )

    latest_users = User.objects.order_by('-date_joined')[:5]

    # Region distribution (top 5)
    from django.db.models import Count as Cnt
    top_regions = (
        House.objects.filter(is_active=True)
        .values('region__name')
        .annotate(c=Cnt('id'))
        .order_by('-c')[:5]
    )

    subscribers_percentage = round((active_subscribers / total_users) * 100) if total_users else 0
    blocked_percentage     = round((blocked_users_count / total_users) * 100) if total_users else 0

    return render(request, 'admin_custom/dashboard.html', {
        'total_users'           : total_users,
        'total_houses'          : total_houses,
        'total_reports'         : total_reports,
        'total_payments'        : total_payments,
        'blocked_users'         : blocked_users_count,
        'new_users_week'        : new_users_week,
        'new_houses_week'       : new_houses_week,
        'active_subscribers'    : active_subscribers,
        'weekly_income'         : weekly_income,
        'monthly_income'        : monthly_income,
        'total_income'          : total_income,
        'reported_users'        : reported_users,
        'latest_payments'       : latest_payments,
        'latest_houses'         : latest_houses,
        'latest_users'          : latest_users,
        'top_regions'           : top_regions,
        'subscribers_percentage': subscribers_percentage,
        'blocked_percentage'    : blocked_percentage,
        'chart_labels'          : chart_labels,
        'chart_income'          : chart_income,
        'chart_users'           : chart_users,
        'chart_houses'          : chart_houses,
    })


@staff_member_required
def admin_houses(request):
    houses = House.objects.select_related('owner', 'region').order_by('-created_at')
    return render(request, 'admin_custom/house_list.html', {'houses': houses})


@staff_member_required
def admin_users(request):
    users = (
        User.objects.annotate(reports_count_attr=Count('received_reports'))
        .order_by('-date_joined')
    )
    return render(request, 'admin_custom/user_list.html', {'users': users})


@staff_member_required
def admin_payments(request):
    payments = Payment.objects.select_related('user', 'tariff').order_by('-created_at')
    return render(request, 'admin_custom/payment_list.html', {'payments': payments})


@staff_member_required
def admin_reports(request):
    reports = (
        Report.objects.select_related('reporter', 'reported_user', 'house')
        .order_by('-created_at')
    )
    return render(request, 'admin_custom/report_list.html', {'reports': reports})


@staff_member_required
def admin_user_block(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, _("Siz o'zingizni bloklay olmaysiz!"))
        return redirect('admin_users')

    user.is_blocked = not user.is_blocked
    if user.is_blocked:
        user.houses.all().delete()
    user.save()
    messages.success(request, _("%(name)s holati o'zgartirildi.") % {'name': user.first_name})
    return redirect('admin_users')


@staff_member_required
def admin_house_delete(request, pk):
    house = get_object_or_404(House, pk=pk)
    house.delete()
    messages.success(request, _("Uy muvaffaqiyatli o'chirildi."))
    return redirect('admin_houses')


@staff_member_required
def admin_user_toggle_block(request, pk):
    user = get_object_or_404(User, pk=pk)

    if user == request.user:
        messages.error(request, _("Siz o'zingizni bloklay olmaysiz!"))
        return redirect('admin_users')

    user.is_blocked = not user.is_blocked

    if user.is_blocked:
        houses_count = user.houses.count()
        user.houses.all().delete()
        user.save()
        messages.warning(
            request,
            _("%(name)s bloklandi va uning %(count)s ta e'loni o'chirib tashlandi.") % {
                'name': user.get_full_name(), 'count': houses_count,
            }
        )
    else:
        user.save()
        messages.success(request, _("%(name)s blokdan chiqarildi.") % {'name': user.get_full_name()})

    return redirect('admin_users')


@staff_member_required
def admin_house_detail(request, pk):
    house = get_object_or_404(
        House.objects.prefetch_related('images', 'comments__user'), pk=pk,
    )
    return render(request, 'admin_custom/house_detail_admin.html', {'house': house})
