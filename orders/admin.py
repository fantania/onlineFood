from django.contrib import admin

from orders.models import Order, OrderedFood, Payment

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(OrderedFood)
