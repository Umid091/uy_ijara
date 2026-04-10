from django.urls import path
from . import views

urlpatterns = [
    path('', views.house_list, name='house_list'),
    path('districts/', views.get_districts, name='get_districts'),
    path('houses/<int:pk>/', views.house_detail, name='house_detail'),
    path('houses/add/', views.house_add, name='house_add'),
    path('houses/<int:pk>/edit/', views.house_edit, name='house_edit'),
    path('houses/<int:pk>/delete/', views.house_delete, name='house_delete'),
    path('houses/<int:pk>/call/', views.call_view, name='call'),
    path('houses/<int:pk>/report/', views.report_view, name='report'),
    path('houses/<int:pk>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('houses/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('houses/<int:pk>/rating/', views.add_rating, name='add_rating'),
    path('images/<int:image_id>/delete/', views.delete_image, name='delete_image'),
]