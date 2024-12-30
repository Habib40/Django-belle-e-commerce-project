from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from cart.models import CartItem
from .forms import OrderForm
from .models import Order,OrderProduct,Payment
from shop.models import ProductColor
import datetime 
from django.contrib import messages
import json
# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import datetime
from .models import  Order, OrderProduct, Payment
from cart .models import CartItem
from .forms import OrderForm

def PlaceOrder(request, total=0, tax=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    grand_total = 0
    for cart_item in cart_items:
        total += (cart_item.product.discount_amount or 0) * cart_item.quantity  # Handle None safely
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create an order instance
            order = Order(
                user=current_user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address_line_1=form.cleaned_data['address_line_1'],
                address_line_2=form.cleaned_data['address_line_2'],
                country=form.cleaned_data['country'],
                state=form.cleaned_data['state'],
                city=form.cleaned_data['city'],
                order_note=form.cleaned_data['order_note'],
                tax=tax,
                ip=request.META.get('REMOTE_ADDR'),
                order_total=grand_total
            )
            order.save()

            # Generate order number
            order_number = f"{datetime.date.today():%Y,%d,%m}{order.id}"
            order.order_number = order_number
            order.save()

            # Create OrderProduct instances
            for cart_item in cart_items:
                color = cart_item.color
                size = cart_item.size
                discount_amount = cart_item.product.discount_amount or 0  # Default to 0 if None

                # Create OrderProduct instance
                OrderProduct.objects.create(
                    order=order,
                    user=current_user,
                    product=cart_item.product,
                    color=color,
                    # tax=tax,
                    # grand_total=grand_total,
                    size=size,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    discount_amount=discount_amount,
                    ordered=True
                )

            # Delete cart items after placing the order
            cart_items.delete()

            # Send a success message to the user
            messages.success(request, 'Your order has been placed successfully!')

            # Redirect to the payments page with order details
            return redirect('payments', order_id=order.id)

        else:
            messages.error(request, 'Please correct the errors in the form.')
            return render(request, 'accounts/checkout.html', {'form': form})

    form = OrderForm()  # Initialize an empty form for GET requests
    return render(request, 'accounts/checkout.html', {'form': form})
def Payments(request, order_id, quantity=0):
    # Fetch the order for the current user
    order = get_object_or_404(Order, id=order_id, user=request.user)
    payment = order.payment if order.is_ordered else None

    # Fetch OrderProduct instances related to the order
    order_products = OrderProduct.objects.filter(order=order)
    
    # Calculate the tax and grand total
    tax = order.tax
    grand_total = order.order_total

    # Initialize subtotal for the entire order
    subtotal = sum(order_product.subtotal() for order_product in order_products)

    if request.method == 'POST':
        body = json.loads(request.body)

        # Create a new payment instance
        payment = Payment(
            user=request.user,
            payment_id=body['transID'],
            payment_method=body['payment_method'],
            amount_paid=grand_total,  # Ensure this is the correct amount
            status=body['status'],
        )
        payment.save()

        # Update the order with the payment information
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Clear the cart after successful payment
        CartItem.objects.filter(user=request.user).delete()

        # Prepare context for rendering the payment confirmation page
        context = {
            'order': order,
            'payment': payment,
            'order_products': order_products,
            'tax': tax,
            'grand_total': grand_total,
            
        }
        return render(request, 'orders/payments.html', context)

    # Prepare context for rendering the payment page
    context = {
        'order': order,
        'payment': payment,
        'order_products': order_products,
        'tax': tax,
        'grand_total': grand_total,
        'subtotal': subtotal,
    }
    return render(request, 'orders/payments.html', context)
    