from datetime import date, datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render

from marketplace.context_processors import get_cart_amounts, get_cart_counter
from marketplace.models import Cart
from menu.models import Category, FoodItem
from vendor.models import OpeningHour, Vendor
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required

def marketplace(request):
    vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)
    vendor_count = vendors.count()
    context = {
          'vendors': vendors,
          'vendor_count': vendor_count,
    }
    return render(request, 'marketplace/listings.html', context)


def vendor_details(request, vendor_slug):
    vendor = get_object_or_404(Vendor, vendor_slug = vendor_slug)
    categories = Category.objects.filter(vendor=vendor).prefetch_related(
        Prefetch(
            'foodItems',
            queryset= FoodItem.objects.filter(is_available=True)
        )
    )
    opening_hours = OpeningHour.objects.filter(vendor=vendor).order_by('day','-from_hour')
    
    # Check current day opening hours
    today_date = date.today()
    today = today_date.isoweekday()

    current_opening_hours = OpeningHour.objects.filter(vendor=vendor, day = today)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
    else:
        cart_items = None

    context ={
        'vendor': vendor,
        'categories': categories,
        'cart_items': cart_items,
        'opening_hours': opening_hours,
        'current_opening_hours': current_opening_hours,
    }
    return render(request, 'marketplace/vendor_details.html', context)
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def add_to_cart(request, food_id):
    if request.user.is_authenticated:
        if is_ajax(request):
            #Check if the food Item exists
            try:
                foodItem = FoodItem.objects.get(id=food_id)
                #Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, foodItem=foodItem)
                    chkCart.quantity +=1
                    chkCart.save()
                    return JsonResponse({
                    'status': 'Success',
                    'message': 'Increased the cart quantity',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity,
                    'cart_amount': get_cart_amounts(request)
                    })
                except:
                    chkCart = Cart.objects.create(user=request.user, foodItem=foodItem, quantity=1)
                    return JsonResponse({
                    'status': 'Success',
                    'message': 'Added the food item to the cart',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity,
                    'cart_amount': get_cart_amounts(request)
                    })
            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'Food Item Not Found!'
                })

        else:
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid Request!'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })
    
def decrease_cart(request, food_id):
    if request.user.is_authenticated:
        if is_ajax(request):
            #Check if the food Item exists
            try:
                foodItem = FoodItem.objects.get(id=food_id)
                #Check if the user has already added that food to the cart
                try:
                    chkCart = Cart.objects.get(user=request.user, foodItem=foodItem)
                    if chkCart.quantity > 1:
                        chkCart.quantity -= 1
                        chkCart.save()
                    else:
                        chkCart.delete()
                        chkCart.quantity = 0
                    return JsonResponse({
                    'status': 'Success',
                    'cart_counter': get_cart_counter(request),
                    'qty': chkCart.quantity,
                    'cart_amount': get_cart_amounts(request)
                    })
                except:
                    return JsonResponse({
                    'status': 'Failed',
                    'message': 'You do not have this item in your cart',
                    })
            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'Food Item Not Found!'
                })

        else:
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid Request!'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })
    
@login_required(login_url='login')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_date')
    context = {
        'cart_items':cart_items
    }
    return render(request, 'marketplace/cart.html', context)

def delete_cart(request,cart_id):
    if request.user.is_authenticated:
        if is_ajax(request):
            try:
                #Check if the cart exists
                cart_item = Cart.objects.get(user=request.user, id=cart_id)
                if cart_item:
                    cart_item.delete()
                    return JsonResponse({
                        'status': 'success',
                        'cart_counter': get_cart_counter(request),
                        'message': "Cart item has been deleted",
                        'cart_amount': get_cart_amounts(request)
                        })
            except:
                return JsonResponse({
                'status': 'Failed',
                'message': 'Cart Item Not Found!'
                })
        else:
            return JsonResponse({
            'status': 'Failed',
            'message': 'Invalid Request!'
            })
    else:
        return JsonResponse({
            'status': 'login_required',
            'message': 'Please login to continue'
        })


    

