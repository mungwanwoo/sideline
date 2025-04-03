from django.db import models

class FoodRecommendation(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=[("local", "주변 맛집"), ("recipe", "레시피")])
    details = models.TextField()
    address = models.CharField(max_length=255, blank=True, null=True)
    is_ad = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.category}"