from rest_framework import serializers
from .models import Food, FoodRestaurant

class FoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = ['id', 'name']

class FoodRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodRestaurant
        fields = ['id', 'food', 'category', 'details', 'address', 'is_ad', 'created_at']