from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from onlineFood_main.settings import PAYPAL_BASE_URL, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import simplejson as json

import base64
import requests


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required(login_url='login')
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by('created_date')
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('marketplace')
    
    subtotal = get_cart_amounts(request)['subtotal']
    tax = get_cart_amounts(request)['tax']
    grand_total = get_cart_amounts(request)['grand_total']
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data['first_name']
            order.last_name = form.cleaned_data['last_name']
            order.phone = form.cleaned_data['phone']
            order.email = form.cleaned_data['email']
            order.address= form.cleaned_data['address']
            order.country = form.cleaned_data['country']
            order.state = form.cleaned_data['state']
            order.city = form.cleaned_data['city']
            order.zip_code = form.cleaned_data['zip_code']
            order.user = request.user
            order.total = grand_total
            order.tax = tax
            order.payment_method = request.POST['payment_method']
            order.save() # order id/pk is generated
            order.order_number = generate_order_number(order.id)
            order.save() # save the generated order number with the id/pk
            context = {
                'order': order,
                'cart_items': cart_items,
            }
            return render(request, 'orders/place_order.html', context)
        else:
            print(form.errors)
        
    return render(request, 'orders/place_order.html')

@login_required(login_url='login')
def payments(request):
    # Check if the request is ajax or not
    if is_ajax(request) and request.method == 'POST':
        # STORE THE PAYMENT DETAILS IN THE PAYMENT MODEL
        order_number = request.POST.get('order_number')
        transaction_id = request.POST.get('transaction_id')
        payment_method = request.POST.get('payment_method')
        status = request.POST.get('status')

        order = Order.objects.get(user=request.user, order_number = order_number)
        payment = Payment(
            user = request.user,
            payment_method = payment_method,
            transaction_id = transaction_id,
            amount = order.total,
            status = status
        )

        payment.save()

        # UPDATE THE ORDER
        order.payment = payment
        order.is_ordered = True
        order.save()

       # MOVE THE CART ITEMS TO ORDERED FOOD MODEL
        cart_items =  Cart.objects.filter(user=request.user)
        for item in cart_items:
            orderder_food = OrderedFood()
            orderder_food.order = order
            orderder_food.payment = payment
            orderder_food.user = request.user
            orderder_food.food_item = item.foodItem
            orderder_food.quantity = item.quantity
            orderder_food.price = item.foodItem.price
            orderder_food.amount = item.foodItem.price * item.quantity # total amount
            orderder_food.save()

        # SEND ORDER CONFIRMATION EMAIL TO THE CUSTOMER
        mail_subject = 'Thank you for your order.'
        mail_template = 'orders/order_confirmation_email.html'
        context = {
            'user': request.user,
            'order': order,
            'to_email': order.email,
        }
        send_notification(mail_subject, mail_template, context)

        # SEND ORDER RECEIVED EMAIL TO THE VENDOR
        mail_subject = 'You have received a new order.'
        mail_template = 'orders/new_order_received.html'
        to_emails = []
        vendor_names = []
        for e in cart_items:
            to_emails.append(e.foodItem.vendor.user.email)
            vendor_names.append(e.foodItem.vendor.user.first_name)
        context = {
            'order': order,
            'to_email': to_emails[0],
            'user': vendor_names[0]
        }
        send_notification(mail_subject, mail_template, context)

        # CLEAR THE CART IF THE PAYMENT IS SUCCESS
        cart_items.delete()

        # RETURN BACK TO AJAX WITH THE STATUS SUCCESS OF FAILURE
        response = {
            'order_number': order_number,
            'transaction_id': transaction_id
        }
        return JsonResponse(response)
    return HttpResponse('Payment view')


def order_complete(request):
    order_number = request.GET.get('order_no')
    transaction_id = request.GET.get('trans_id')

    try:
        order = Order.objects.get(order_number=order_number, payment__transaction_id=transaction_id, is_ordered=True)
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)

        tax_data = json.loads(order.tax_data)
        print(tax_data)
        context = {
            'order': order,
            'ordered_food': ordered_food,
            'subtotal': subtotal,
            'tax_data': tax_data,
        }
        return render(request, 'orders/order_complete.html', context)
    except:
        return redirect('home')


def generate_paypal_access_token():
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError("MISSING_API_CREDENTIALS")

    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(f"{PAYPAL_BASE_URL}/v1/oauth2/token", headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Failed to generate Access Token: {response.status_code} - {response.text}")
        return None
    

@csrf_exempt 
def create_order(request):
        
    if request.method == 'POST':
        try:
            # Generate PayPal access token (similar to generateAccessToken in server.js)

            access_token = generate_paypal_access_token() 
            grand_total = get_cart_amounts(request)['grand_total']

            # Prepare payload for PayPal order creation
            payload = {
                "intent": "CAPTURE",
                "purchase_units": [
                    {
                        "amount": {
                            "currency_code": "USD",  # Adjust currency as needed
                            "value": str(grand_total), # Assuming 'order' object is available in this view
                        },
                    }
                ],
            }

            # Make the API call to create the order
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.post("https://api-m.sandbox.paypal.com/v2/checkout/orders", headers=headers, json=payload)

            # Handle the response and return appropriate status and data
            return JsonResponse(response.json(), status=response.status_code) 

        except Exception as e:
            return JsonResponse({"error": "Failed to create order."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405)  # Handle non-POST requests


@csrf_exempt 
def capture_order(request, order_id):
    if request.method == 'POST':
        try:

            # Generate PayPal access token
            access_token = generate_paypal_access_token()

            # Make the API call to capture the order
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            }
            response = requests.post(f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{order_id}/capture", headers=headers)


            # Handle the response and return appropriate status and data
            return JsonResponse(response.json(), status=response.status_code)
        

        except Exception as e:
            return JsonResponse({"error": "Failed to capture order."}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=405) 

def generate_paypal_access_token():
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError("MISSING_API_CREDENTIALS")

    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials"
    }

    response = requests.post(f"{PAYPAL_BASE_URL}/v1/oauth2/token", headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        print(f"Failed to generate Access Token: {response.status_code} - {response.text}")
        return None