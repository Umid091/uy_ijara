from django.contrib import admin
from .models import Region, District, House, HouseImage, HouseRating, Comment, Wishlist, Report


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')


@admin.register(House)
class HouseAdmin(admin.ModelAdmin):
    list_display  = ('full_address', 'price_usd', 'owner', 'is_active', 'created_at')
    list_filter   = ('is_active', 'region', 'district')
    search_fields = ('full_address', 'street')


@admin.register(HouseImage)
class HouseImageAdmin(admin.ModelAdmin):
    list_display = ('house', 'is_main', 'order')


@admin.register(HouseRating)
class HouseRatingAdmin(admin.ModelAdmin):
    list_display = ('house', 'user', 'score')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('house', 'user', 'created_at')


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'house', 'created_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'house', 'created_at')