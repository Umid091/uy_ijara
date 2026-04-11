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
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-dashboard/houses/', views.admin_houses, name='admin_houses'),
    path('admin-dashboard/users/', views.admin_users, name='admin_users'),
    path('admin-dashboard/payments/', views.admin_payments, name='admin_payments'),
    path('admin-dashboard/reports/', views.admin_reports, name='admin_reports'),
    path('admin-dashboard/user/<int:pk>/toggle-block/', views.admin_user_toggle_block, name='admin_user_toggle_block'),
    path('admin-dashboard/houses/<int:pk>/detail/', views.admin_house_detail, name='admin_house_detail'),
    # Amallar (Bloklash, O'chirish)
    path('admin-dashboard/users/<int:pk>/block/', views.admin_user_block, name='admin_user_block'),
    path('admin-dashboard/houses/<int:pk>/delete/', views.admin_house_delete, name='admin_house_delete'),
    # SHU QATORNI QO'SHISH KERAK
]