from django.db import models

class Food(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class FoodRestaurant(models.Model):
    food = models.ForeignKey(Food, on_delete=models.CASCADE, related_name="recommendations")
    restaurant = models.TextField()
    address = models.CharField(max_length=255, blank=True, null=True)
    is_ad = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food.name} - {self.category}"