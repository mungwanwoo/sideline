from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_food, name='recommend_food'),
    path('get_weather/', views.get_weather, name='get_weather'),
]