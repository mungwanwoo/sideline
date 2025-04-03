from django.urls import path
from . import views

urlpatterns = [
    path('recommend/', views.recommend_food, name='recommend_food'),
]