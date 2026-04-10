from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    phone       = models.CharField(max_length=20, unique=True)
    avatar      = models.ImageField(upload_to='avatars/', null=True, blank=True)
    balance     = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_blocked  = models.BooleanField(default=False)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    card_holder = models.CharField(max_length=100, null=True, blank=True)
    card_expiry = models.CharField(max_length=7, null=True, blank=True)  # MM/YYYY
    created_at  = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = 'phone'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name        = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'

    def __str__(self):
        return f"{self.get_full_name()} ({self.phone})"

    @property
    def active_subscription(self):
        return self.subscriptions.filter(
            is_active=True,
            end_date__gte=timezone.now()
        ).first()

    @property
    def has_active_subscription(self):
        return self.active_subscription is not None

    @property
    def report_count(self):
        return self.received_reports.count()


class Tariff(models.Model):
    name          = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    price         = models.DecimalField(max_digits=10, decimal_places=2)
    is_active     = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Tarif'
        verbose_name_plural = 'Tariflar'
        ordering            = ['duration_days']

    def __str__(self):
        return f"{self.name} — {self.price} so'm"


class UserSubscription(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    tariff     = models.ForeignKey(Tariff, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date   = models.DateTimeField()
    is_active  = models.BooleanField(default=True)

    class Meta:
        verbose_name        = 'Obuna'
        verbose_name_plural = 'Obunalar'
        ordering            = ['-start_date']

    def __str__(self):
        return f"{self.user} — {self.tariff.name} ({self.end_date.date()})"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.end_date = timezone.now() + timezone.timedelta(days=self.tariff.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.end_date

    @property
    def days_left(self):
        delta = self.end_date - timezone.now()
        return max(delta.days, 0)


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Kutilmoqda'
        SUCCESS = 'success', 'Muvaffaqiyatli'
        FAILED  = 'failed',  'Xato'

    user               = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    tariff             = models.ForeignKey(Tariff, on_delete=models.PROTECT, related_name='payments')
    subscription       = models.OneToOneField(
                            UserSubscription, on_delete=models.SET_NULL,
                            null=True, blank=True, related_name='payment'
                         )
    amount             = models.DecimalField(max_digits=10, decimal_places=2)
    card_number_masked = models.CharField(max_length=20)   # **** **** **** 1234
    status             = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.amount} so'm ({self.status})"


class Notification(models.Model):
    class Type(models.TextChoices):
        SUBSCRIPTION_2DAY = 'sub_2day', 'Tarifga 2 kun qoldi'
        SUBSCRIPTION_1DAY = 'sub_1day', 'Tarifga 1 kun qoldi'
        SUBSCRIPTION_END  = 'sub_end',  'Tarif tugadi'
        REPORT_RECEIVED   = 'report',   'Shikoyat olindi'
        GENERAL           = 'general',  'Umumiy'

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type       = models.CharField(max_length=20, choices=Type.choices, default=Type.GENERAL)
    title      = models.CharField(max_length=200)
    message    = models.TextField()
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Bildirishnoma'
        verbose_name_plural = 'Bildirishnomalar'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.user} — {self.title}"