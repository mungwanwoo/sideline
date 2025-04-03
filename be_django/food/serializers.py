from rest_framework import serializers
from .models import FoodRecommendation

class FoodRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodRecommendation
        fields = ['name', 'category', 'details', 'address', 'is_ad', 'created_at']