from django.shortcuts import render,redirect,get_object_or_404,HttpResponseRedirect
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
from decimal import Decimal,InvalidOperation
from django.template.loader import render_to_string
from xhtml2pdf import pisa  # Make sure to import the necessary library
from django.template import Context
from django.template.loader import get_template
import logging
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import stripe
# views.py
from django.http import JsonResponse
from django.views import View
import requests
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from cart.models import Cart , CartItem
from promotions.models import Coupon
from cart.views import calculate_totals 
import uuid
from cart.views import _cart_id
from django.http import Http404
# from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site

# stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

def PlaceOrder(request, total=0, tax=0, quantity=0):
    current_user = request.user
    is_guest = not current_user.is_authenticated
    
    # Get cart items based on user status
    if is_guest:
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id, is_guest=True).first()
        cart_items = list(CartItem.objects.filter(cart=cart, is_active=True)) if cart else []
        # Prevent coupon usage for guest users
        if cart and cart.coupon:
            messages.info(request, "Coupons are only available for registered users.")
            cart.coupon = None
            cart.save()
    else:
        cart = Cart.objects.filter(user=current_user).first()
        cart_items = list(CartItem.objects.filter(user=current_user, is_active=True))

    # Check if cart is empty
    if len(cart_items) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('store')

    # Calculate totals
    subtotal = sum(item.quantity * item.product.price for item in cart_items)
    tax = (Decimal(0.02) * subtotal) / Decimal(100)  # 2% tax
    grand_total = subtotal + tax

    # Handle POST request
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Create Order
            order_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],  # Email stored in Order table
                'phone': form.cleaned_data['phone'],
                'address_line_1': form.cleaned_data['address_line_1'],
                'address_line_2': form.cleaned_data['address_line_2'],
                'country': form.cleaned_data['country'],
                'state': form.cleaned_data['state'],
                'city': form.cleaned_data['city'],
                'order_note': form.cleaned_data['order_note'],
                'order_total': float(grand_total),
                'tax': float(tax),
                'ip': request.META.get('REMOTE_ADDR'),
                'payment_method': request.POST.get('payment_method', 'credit_card'),
                'cash_on_delivery': request.POST.get('cash_on_delivery', 'off') == 'on',
            }
            
            if not is_guest:
                order_data['user'] = current_user
            
            order = Order.objects.create(**order_data)
            order.order_number = f"{datetime.date.today():%Y%m%d}-{order.id}"
            order.save()

            # Create OrderProducts
            can_create_order = True
            for cart_item in cart_items:
                if cart_item.quantity > cart_item.product.quantity_left:
                    messages.error(request, f"Not enough stock for {cart_item.product.title}.")
                    can_create_order = False
                    break

                OrderProduct.objects.create(
                    order=order,
                    user=current_user if not is_guest else None,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    product_price=cart_item.product.price,
                    color=cart_item.color,
                    size=cart_item.size,
                    ordered=True
                )

                # Update stock
                product = cart_item.product
                product.quantity_left -= cart_item.quantity
                product.save()

            if can_create_order:
                # Clear cart items
                if is_guest:
                    if cart:
                        cart.delete()
                    if 'cart_id' in request.session:
                        del request.session['cart_id']
                    # Store guest email in session for future reference
                    request.session['guest_email'] = form.cleaned_data['email']
                else:
                    CartItem.objects.filter(user=current_user).delete()
                    if cart:
                        cart.delete()
                
                messages.success(request, 'Order placed successfully!')
                # Redirect to order success page instead of dashboard
                return redirect('payments', order_id=order.id)
        else:
            messages.error(request, 'Please correct the errors in the form.')

    # For GET request
    initial_data = {}
    if not is_guest and current_user:
        initial_data = {
            'first_name': current_user.first_name,
            'last_name': current_user.last_name,
            'email': current_user.email,
            'phone': current_user.phone_number,
        }

    form = OrderForm(initial=initial_data)
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'grand_total': grand_total,
        'is_guest': is_guest,
    }
    return render(request, 'accounts/checkout.html', context)


# @login_required(login_url='login')
# def PlaceOrder(request, total=0, tax=0, quantity=0):
#     current_user = request.user
#     cart_items = CartItem.objects.filter(user=current_user)

#     if not cart_items.exists():
#         messages.warning(request, "Your cart is empty.")
#         return redirect('store')

#     # Fetch cart and coupon
#     cart = Cart.objects.filter(user=current_user).first()
#     coupon = cart.coupon if cart and cart.coupon else None

#     # Calculate base subtotal (without any discounts)
#     subtotal = sum(item.quantity * item.product.price for item in cart_items)
    
#     # Calculate coupon discount (applied to subtotal)
#     coupon_discount = Decimal(0)
#     if coupon:
#         coupon_discount = (coupon.discount / Decimal(100)) * subtotal
#         coupon_discount = min(coupon_discount, subtotal)  # Ensure discount doesn't exceed subtotal

#     # Distribute coupon discount proportionally (without rounding)
#     distributed_coupon = {}
#     remaining_discount = coupon_discount
#     for i, item in enumerate(cart_items):
#         item_total = item.quantity * item.product.price
#         if i == len(cart_items) - 1:
#             # Assign remaining discount to the last item
#             distributed_coupon[item.id] = remaining_discount
#         else:
#             # Calculate exact proportional discount
#             item_coupon_discount = (item_total / subtotal) * coupon_discount
#             distributed_coupon[item.id] = item_coupon_discount
#             remaining_discount -= item_coupon_discount

#     # Calculate totals after discount
#     total_after_discount = subtotal - coupon_discount
#     tax = (Decimal(2) * total_after_discount) / Decimal(100)  # Example: 2% tax
#     grand_total = total_after_discount + tax

#     # Handle POST request (order creation)
#     if request.method == 'POST':
#         form = OrderForm(request.POST)
#         if form.is_valid():
#             # Create Order
#             order = Order(
#                 user=current_user,
#                 first_name=form.cleaned_data['first_name'],
#                 last_name=form.cleaned_data['last_name'],
#                 email=form.cleaned_data['email'],
#                 phone=form.cleaned_data['phone'],
#                 address_line_1=form.cleaned_data['address_line_1'],
#                 address_line_2=form.cleaned_data['address_line_2'],
#                 country=form.cleaned_data['country'],
#                 state=form.cleaned_data['state'],
#                 city=form.cleaned_data['city'],
#                 order_note=form.cleaned_data['order_note'],
#                 order_total=grand_total,
#                 tax=tax,
#                 ip=request.META.get('REMOTE_ADDR'),
#                 discount=coupon_discount,
#             )
#             order.save()
#             order.order_number = f"{datetime.date.today():%Y%d%m}-{order.id}"
#             order.save()

#             # Validate stock and create OrderProduct entries
#             can_create_order = True
#             for cart_item in cart_items:
#                 if cart_item.quantity > cart_item.product.quantity_left:
#                     messages.error(request, f"Not enough stock for {cart_item.product.title}.")
#                     can_create_order = False
#                     break

#                 # Calculate final price per item (after coupon discount)
#                 item_total = cart_item.quantity * cart_item.product.price
#                 item_coupon_discount = distributed_coupon.get(cart_item.id, Decimal('0.00'))
#                 final_price = item_total - item_coupon_discount

#                 # Create OrderProduct - MAKE SURE TO INCLUDE USER!
#                 OrderProduct.objects.create(
#                     order=order,
#                     user=current_user,  # THIS WAS MISSING IN YOUR ORIGINAL CODE
#                     product=cart_item.product,
#                     quantity=cart_item.quantity,
#                     product_price=cart_item.product.price,
#                     coupon_discount=item_coupon_discount,
#                     discount_amount=final_price,
#                     color=cart_item.color,  # Include if your model has these
#                     size=cart_item.size,    # Include if your model has these
#                     ordered=True
#                 )

#             if can_create_order:
#                 cart_items.delete()
#                 if coupon:  # Clear coupon after use if needed
#                     cart.coupon = None
#                     cart.save()
#                 messages.success(request, 'Order placed successfully!')
#                 return redirect('payments', order_id=order.id)
#         else:
#             messages.error(request, 'Form errors. Please correct them.')

#     # Render checkout page (GET request)
#     form = OrderForm()
#     context = {
#         'form': form,
#         'cart_items': cart_items,
#         'grand_total': grand_total,
#     }
#     return render(request, 'accounts/checkout.html', context)

def Payments(request, order_id):
    try:
        # Authenticate order access
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=order_id, user=request.user)
        else:
            order = get_object_or_404(Order, id=order_id, user__isnull=True)

        # Get order products with product data
        order_products = OrderProduct.objects.filter(order=order).select_related('product')

        # Calculate subtotal using discount_amount if available, otherwise regular price
        subtotal = Decimal('0.00')
        for item in order_products:
            # Use discount_amount as the price if available, otherwise use regular price
            item_price = Decimal(str(item.product.discount_amount)) if item.product.discount_amount else Decimal(str(item.product.price))
            subtotal += item_price * Decimal(str(item.quantity))

        # Calculate tax (2% of subtotal)
        tax = (subtotal * Decimal('0.02')).quantize(Decimal('0.00'))

        # Calculate grand total (subtotal + tax)
        grand_total = (subtotal + tax).quantize(Decimal('0.00'))

        # Update order totals in database
        order.sub_total = subtotal
        order.tax = tax
        order.order_total = grand_total  # Includes tax
        order.save()

        context = {
            'order': order,
            'order_products': order_products,
            'payment': order.payment if hasattr(order, 'payment') else None,
            'sub_total': subtotal,  # Before tax
            'tax': tax,
            'grand_total': grand_total,  # After tax
            'is_guest': not request.user.is_authenticated
        }
        if request.method == 'POST':
            try:
                payment_method = request.POST.get('payment_method')
                if not payment_method:
                    messages.error(request, "Please select a payment method")
                    return render(request, 'orders/payments.html', context)

                order.payment_method = payment_method

                if payment_method == 'cash_on_delivery':
                    order.cash_on_delivery = True
                    order.is_ordered = True
                    order.status = 'Pending'
                    order.save()

                    # Reduce product quantities
                    for order_product in order_products:
                        product = order_product.product
                        product.stock -= order_product.quantity
                        product.save()

                    messages.success(request, "Order placed successfully!")

                    if request.user.is_authenticated:
                        return redirect('dashboard')
                    else:
                        return redirect('order_success', order_id=order.id)

                elif payment_method in ['credit_card', 'paypal']:
                    order.save()
                    return redirect('create_payment', order_id=order.id)
                else:
                    messages.error(request, "Invalid payment method selected")
                    return render(request, 'orders/payments.html', context)

            except Exception as e:
                print(f"Payment processing error: {str(e)}")
                messages.error(request, "Failed to process payment. Please try again.")
                return render(request, 'orders/payments.html', context)

        return render(request, 'orders/payments.html', context)

    except Exception as e:
        print(f"Order processing error: {str(e)}")
        messages.error(request, "An error occurred while processing your order.")
        return redirect('store') # Always return a response
#     # Fetch the order for the current user
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     payment = order.payment if order.is_ordered else None

#     # Fetch OrderProduct instances related to the order
#     order_products = OrderProduct.objects.filter(order=order)
#     sub_total = Decimal('0.00')  # Initialize total subtotal as Decimal

#     for order_product in order_products:
#         # Ensure discount amount is Decimal and handle potential errors
#         try:
#             discount_amount = Decimal(order_product.discount_amount)  # Ensure it's Decimal
#         except (ValueError, InvalidOperation) as e:
#             print(f"Invalid discount amount: {order_product.discount_amount}, Error: {e}")
#             discount_amount = Decimal('0.00')  # Set to zero or handle accordingly

#         # Ensure quantity is Decimal and handle potential errors
#         try:
#             quantity = Decimal(order_product.quantity)  # Ensure quantity is Decimal
#         except (ValueError, InvalidOperation) as e:
#             print(f"Invalid quantity: {order_product.quantity}, Error: {e}")
#             quantity = Decimal('0.00')  # Set to zero or handle accordingly

#         # Calculate subtotal for each order_product
#         order_product.sub_total = discount_amount * quantity
#         sub_total += order_product.sub_total  # Add to total subtotal

#     # Calculate tax and grand total
#     tax_rate = Decimal('0.02')  # Use Decimal for tax rate
#     tax = sub_total * tax_rate  # Calculate tax
#     grand_total = sub_total + tax  # Grand total is subtotal plus tax

#     # Prepare context for rendering the payment page
#     context = {
#         'order': order,
#         'payment': payment,
#         'order_products': order_products,
#         'tax': tax,
#         'grand_total': round(grand_total),
#         'sub_total': sub_total,
#     }

#     # Check if the form is submitted with a payment method
#     if request.method == 'POST':
#         payment_method = request.POST.get('payment_method')
#         order.payment_method = payment_method  # Save payment method

#         # Handle cash on delivery
#         if payment_method == 'cash_on_delivery':
#             order.cash_on_delivery = True  # Set cash on delivery
#             order.is_ordered = True  # Mark the order as completed
#             order.save()  # Save the order

#             # Redirect to the dashboard or a confirmation page
#             return redirect('dashboard')

#         # For other payment methods, add logic if needed

#     return render(request, 'orders/payments.html', context)


# def order_success(request, order_id):
#     # Get the order
#     if request.user.is_authenticated:
#         order = Order.objects.filter(id=order_id, user=request.user).first()
#     else:
#         order = Order.objects.filter(id=order_id, user__isnull=True).first()
    
#     order_products = OrderProduct.objects.filter(order=order)
    
#     # Calculate subtotal (sum of item prices × quantities)
#     sub_total = Decimal('0.00')
#     for item in order_products:
#         sub_total += Decimal(str(item.product_price)) * Decimal(str(item.quantity))
    
#     # Calculate 2% tax from the subtotal
#     tax = sub_total * Decimal('0.02')
    
#     # Get the existing grand total (or use subtotal + tax if not set)
#     grand_total = order.order_total if order.order_total else (sub_total + tax)
    
#     # Update the order with all calculated values
#     order.sub_total = sub_total - tax
#     order.tax = tax  # Store the calculated 2% tax
#     order.order_total = grand_total
#     order.save()
    
#     # Send confirmation email
#     send_confirmation_email(request, order, order_products, sub_total, tax, grand_total)

#     context = {
#         'order': order,
#         'order_products': order_products,
#         'sub_total': sub_total,
#         'tax': tax,
#         'grand_total': grand_total,
#         'is_guest': not request.user.is_authenticated
#     }
    
#     return render(request, 'orders/order_success.html', context)

def order_success(request, order_id):
    # Get the order
    if request.user.is_authenticated:
        order = Order.objects.filter(id=order_id, user=request.user).first()
    else:
        order = Order.objects.filter(id=order_id, user__isnull=True).first()
    
    if not order:
        return redirect('store')
    
    order_products = OrderProduct.objects.filter(order=order).select_related('product')
    
    # Initialize totals
    sub_total = Decimal('0.00')
    regular_total = Decimal('0.00')
    
    # Calculate using discount_amount as the actual price
    for item in order_products:
        # Use discount_amount if available, otherwise use regular price
        selling_price = Decimal(str(item.product.discount_amount)) if item.product.discount_amount else Decimal(str(item.product.price))
        
        # Store both prices for display
        item.selling_price = selling_price
        item.regular_price = Decimal(str(item.product.price))
        
        # Calculate line total
        item.sub_total = selling_price * Decimal(str(item.quantity))
        item.regular_sub_total = item.regular_price * Decimal(str(item.quantity))
        
        # Add to totals
        sub_total += item.sub_total
        regular_total += item.regular_sub_total
    
    # Calculate discount amount (regular total - discounted total)
    total_discount = regular_total - sub_total
    
    # Calculate tax (2% of subtotal)
    tax = sub_total * Decimal('0.02')
    
    # Grand total is discounted subtotal + tax
    grand_total = sub_total + tax
    
    # Update the order with calculated values
    order.sub_total = sub_total
    order.tax = tax
    order.discount = total_discount
    order.order_total = grand_total
    order.save()
    send_confirmation_email(request, order, order_products, sub_total, tax, grand_total)
    
    # Prepare context
    context = {
        'order': order,
        'order_products': order_products,
        'sub_total': sub_total,
        'regular_total': regular_total,
        'total_discount': total_discount,
        'tax': tax,
        'grand_total': grand_total,
        'is_guest': not request.user.is_authenticated
    }
    
    return render(request, 'orders/order_success.html', context)
def send_confirmation_email(request, order, order_products, sub_total, tax, grand_total):
    """
    Send order confirmation email with properly formatted product images
    """
    subject = f"Order Confirmation #{order.order_number or order.id}"
    current_site = get_current_site(request)
    domain = current_site.domain
    
    # Prepare products with enhanced data including absolute image URLs
    enhanced_products = []
    for item in order_products:
        product_data = {
            'name': item.product.title,
            'quantity': item.quantity,
            'price': item.product_price,
            'image_url': f"https://{domain}{item.product.images.url}" if item.product.images else None,
            'product': item.product  # Keep reference to original product if needed
        }
        enhanced_products.append(product_data)
    
    # Render HTML email template
    html_message = render_to_string('orders/order_confirmation_email.html', {
        'order': order,
        'order_products': enhanced_products,  # Use the enhanced list with image URLs
        'sub_total': sub_total,
        'tax': tax,
        'grand_total': grand_total,
        'domain': domain,
        'logo_url': f"https://{domain}/static/images/logo.png"  # Example for logo
    })
    
    # Create plain text version
    plain_message = strip_tags(html_message)
    
    # Create and send email
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email='habibkb5080@gmail.com',
            to=[order.email],
            reply_to=['support@yourdomain.com'],
            headers={'X-Entity-Ref-ID': str(order.id)}  # For email tracking
        )
        email.attach_alternative(html_message, "text/html")
        email.send()
        
        # Log successful email delivery
        logger.info(f"Order confirmation sent for order #{order.id} to {order.email}")
        
    except Exception as e:
        logger.error(f"Failed to send order confirmation for order #{order.id}: {str(e)}")
        # Consider implementing a retry mechanism here

class CreatePaymentView(View):
    def get(self, request, order_id):
        
        order = get_object_or_404(Order, id=order_id)
        
        
        success_url = request.build_absolute_uri(reverse('payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

        return render(request, 'orders/payment_form.html', {
            'success_url': success_url,
            'cancel_url': cancel_url,
            'amount': order.order_total,
            'cus_name': f"{order.first_name} {order.last_name}",
            'cus_email': order.email,
            'order': order
        })

    def post(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)

        # Prepare payload for payment API
        success_url = request.build_absolute_uri(reverse('payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

        payload = {
            "cus_name": f"{order.first_name} {order.last_name}",
            "cus_email": order.email,
            "amount": str(order.order_total),
            "success_url": success_url,
            "cancel_url": cancel_url,
            "webhook_url": "https://yourdomain.com/webhook",
            "meta_data": json.dumps({"phone": order.phone})
        }
        headers = {
            'API-KEY': settings.IT_PAY_BD_API_KEY,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(
                "https://pay.itpaybd.xyz/api/payment/create",
                headers=headers,
                json=payload
            )
            response_data = response.json()
            if response.ok and "payment_url" in response_data:
                payment_url = response_data.get("payment_url")
                return JsonResponse({
                    "status": 1,
                    "payment_url": payment_url,
                    "message": "Payment link created successfully."
                })
            else:
                return JsonResponse({
                    "status": "error",
                    "message": response_data.get("message", "Payment gateway error.")
                })

        except Exception as e:
            logger.error(f"Error communicating with payment gateway: {str(e)}")
            return JsonResponse({
                "status": "error",
                "message": "An error occurred while processing your payment."
            })
class SuccessView(View):
    def get(self, request):
        print(request.GET)
        transaction_id = request.GET.get('transactionId')
        payment_method = request.GET.get('paymentMethod', 'Unknown')
        amount = request.GET.get('paymentAmount')
        status = request.GET.get('status', '').lower()

        if not transaction_id:
            logger.error("Transaction ID is missing.")
            return render(request, 'orders/cancel.html', {
                'message': "Transaction ID is required."
            })
        
        
         # Create a new Payment record
        payment = Payment(
            user=request.user,
            payment_id=transaction_id,
            payment_method=payment_method,
            amount_paid=request.GET.get('paymentAmount'),  # Ensure it's converted to float
            status=status,
            # payment_fee = str(payment_fee)
        )
        payment.save()

        if status == "completed" :
            return render(request, 'orders/success.html', {
                'transaction_id': transaction_id,
                'payment_method': payment_method,
                'amount': amount,
                'status': "Success"
            })
        else:
            return render(request, 'orders/cancel.html', {
                'message': f"Payment failed or verification unsuccessful for transaction ID: {transaction_id}."
            })

    

def payment_cancel(request):
    return HttpResponse
def generate_invoice(request, order_id):
    # Get the order using the order_id
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Ensure user ownership
    order_products = OrderProduct.objects.filter(order=order).select_related('product')
    # Create a list of products with absolute image URLs
    for order_product in order_products:
        order_product.product.image_url = request.build_absolute_uri(order_product.product.images.url)
    else:
        order_product.product.image_url = None  # or a default image
    # Create a context for the template
    context = {
        'order': order,
        'order_products': order_products,
        'request': request,
    }

    # Render the template to a string for PDF generation
    html = render_to_string('orders/invoice.html', context)
    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response, context={'base_url': request.build_absolute_uri('/')})
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response

