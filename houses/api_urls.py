from django.urls import path

from . import api

urlpatterns = [
    path('houses/',                  api.api_houses,           name='api_houses'),
    path('houses/<int:pk>/',         api.api_house_detail,     name='api_house_detail'),
    path('houses/<int:pk>/wishlist/', api.api_toggle_wishlist, name='api_toggle_wishlist'),
    path('regions/',                 api.api_regions,          name='api_regions'),
    path('districts/',               api.api_districts,        name='api_districts'),
    path('me/',                      api.api_me,               name='api_me'),
]
