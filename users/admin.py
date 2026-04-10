from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Tariff, UserSubscription, Payment, Notification


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ('phone', 'first_name', 'last_name', 'balance', 'is_blocked', 'created_at')
    list_filter   = ('is_blocked', 'is_staff')
    search_fields = ('phone', 'first_name', 'last_name')
    ordering      = ('-created_at',)

    fieldsets = UserAdmin.fieldsets + (
        ("Qo'shimcha", {
            'fields': ('phone', 'avatar', 'balance', 'is_blocked', 'card_number', 'card_holder', 'card_expiry')
        }),
    )


@admin.register(Tariff)
class TariffAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration_days', 'price', 'is_active')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'tariff', 'start_date', 'end_date', 'is_active')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'tariff', 'amount', 'status', 'created_at')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type', 'title', 'is_read', 'created_at')