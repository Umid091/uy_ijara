from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name        = 'Viloyat'
        verbose_name_plural = 'Viloyatlar'
        ordering            = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='districts')
    name   = models.CharField(max_length=100)

    class Meta:
        verbose_name        = 'Tuman'
        verbose_name_plural = 'Tumanlar'
        ordering            = ['name']
        unique_together     = ('region', 'name')

    def __str__(self):
        return f"{self.name}, {self.region.name}"


class House(models.Model):
    owner        = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='houses')
    region       = models.ForeignKey(Region, on_delete=models.PROTECT, related_name='houses')
    district     = models.ForeignKey(District, on_delete=models.PROTECT, related_name='houses')
    street       = models.CharField(max_length=200)
    full_address = models.TextField()
    latitude     = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude    = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    price_usd    = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description  = models.TextField()
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Uy'
        verbose_name_plural = 'Uylar'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.full_address} — ${self.price_usd}"

    @property
    def average_rating(self):
        result = self.ratings.aggregate(avg=models.Avg('score'))
        return round(result['avg'], 1) if result['avg'] else 0

    @property
    def main_image(self):
        return self.images.filter(is_main=True).first() or self.images.first()


class HouseImage(models.Model):
    house   = models.ForeignKey(House, on_delete=models.CASCADE, related_name='images')
    image   = models.ImageField(upload_to='houses/')
    is_main = models.BooleanField(default=False)
    order   = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Uy rasmi'
        verbose_name_plural = 'Uy rasmlari'
        ordering            = ['order']

    def __str__(self):
        return f"{self.house} — rasm {self.order}"


class HouseRating(models.Model):
    house      = models.ForeignKey(House, on_delete=models.CASCADE, related_name='ratings')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ratings')
    score      = models.PositiveSmallIntegerField(
                    validators=[MinValueValidator(1), MaxValueValidator(5)]
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Reyting'
        verbose_name_plural = 'Reytinglar'
        unique_together     = ('house', 'user')

    def __str__(self):
        return f"{self.user} → {self.house}: {self.score}⭐"


class Comment(models.Model):
    house      = models.ForeignKey(House, on_delete=models.CASCADE, related_name='comments')
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Izoh'
        verbose_name_plural = 'Izohlar'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.user} → {self.house} ({self.created_at.date()})"


class Wishlist(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist')
    house      = models.ForeignKey(House, on_delete=models.CASCADE, related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Saqlangan uy'
        verbose_name_plural = 'Saqlangan uylar'
        unique_together     = ('user', 'house')

    def __str__(self):
        return f"{self.user} → {self.house}"


class Report(models.Model):
    reporter      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_reports')
    reported_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reports')
    house         = models.ForeignKey(House, on_delete=models.SET_NULL, null=True, related_name='reports')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Shikoyat'
        verbose_name_plural = 'Shikoyatlar'
        unique_together     = ('reporter', 'house')
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.reporter} → {self.reported_user} ({self.created_at.date()})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.reported_user.received_reports.count() >= 5:
            self.reported_user.is_blocked = True
            self.reported_user.save(update_fields=['is_blocked'])
            self.reported_user.houses.all().delete()