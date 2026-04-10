from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register_view, name='register'),
    path('login/',views.login_view,name='login'),
    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile_view,  name='profile'),
    path('profile/edit/',views.profile_edit_view, name='profile_edit'),
    path('balance/top-up/',views.top_up_balance_view,name='top_up_balance'),
    path('tariffs/',views.tariff_list_view, name='tariff_list'),
    path('tariffs/<int:tariff_id>/buy/',views.buy_tariff_view,name='buy_tariff'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('notifications/read/',views.mark_notifications_read, name='notifications_read'),
    path('my-houses/', views.my_houses_view, name='my_houses'),
]