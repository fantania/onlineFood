from django.contrib import admin

from marketplace.models import Cart

class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'foodItem', 'quantity', 'updated_date')


admin.site.register(Cart,CartAdmin)
