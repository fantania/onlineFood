import decimal
from marketplace.models import Cart
from menu.models import FoodItem


def get_cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        try:
            cart_items = Cart.objects.filter(user=request.user)
            if cart_items:
                for cart_item in cart_items:
                    cart_count += cart_item.quantity
            else:
                cart_count = 0
        except:
            cart_count = 0

    return dict(cart_count=cart_count)

def get_cart_amounts(request):
    subtotal = 0
    tax = 0
    transaction = 0
    delivery = 10
    grand_total = 0
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            foodItem = FoodItem.objects.get(pk=item.foodItem.id)
            subtotal += (foodItem.price * item.quantity)
        tax = round(subtotal * 7/100, 2)
        grand_total = float(subtotal + transaction + tax + delivery)
        transaction = round(grand_total*(float(2.9/100)) + float(0.30), 2)
    return dict(subtotal = subtotal, tax = tax, grand_total = grand_total, transaction = transaction, delivery = delivery)
