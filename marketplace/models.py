from django.db import models

from accounts.models import User
from menu.models import FoodItem

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    foodItem = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveBigIntegerField()
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now = True)

    def __unicode__(self):
        return self.user
