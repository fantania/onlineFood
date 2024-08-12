from django.http import HttpResponse
from django.shortcuts import redirect, render

from marketplace.context_processors import get_cart_amounts
from marketplace.models import Cart
from orders.forms import OrderForm
from orders.models import Order, OrderedFood, Payment
from orders.utils import generate_order_number
from accounts.utils import send_notification
from django.contrib.auth.decorators import login_required


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
    transaction = get_cart_amounts(request)['transaction']
    delivery = get_cart_amounts(request)['delivery']
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
        return HttpResponse('Success')
    return HttpResponse('Payment view')
