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

# stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)

@login_required(login_url='login')

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
            order.save()  # Save the order first to get the ID
            order.order_number = f"{datetime.date.today():%Y%d%m}-{order.id}"  # Use a more unique format
            order.save()  # Save again to update the order number

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
    sub_total = Decimal('0.00')  # Initialize total subtotal as Decimal

    for order_product in order_products:
        # Ensure discount amount is Decimal and handle potential errors
        try:
            discount_amount = Decimal(order_product.discount_amount)  # Ensure it's Decimal
        except (ValueError, InvalidOperation) as e:
            print(f"Invalid discount amount: {order_product.discount_amount}, Error: {e}")
            discount_amount = Decimal('0.00')  # Set to zero or handle accordingly

        # Ensure quantity is Decimal and handle potential errors
        try:
            quantity = Decimal(order_product.quantity)  # Ensure quantity is Decimal
        except (ValueError, InvalidOperation) as e:
            print(f"Invalid quantity: {order_product.quantity}, Error: {e}")
            quantity = Decimal('0.00')  # Set to zero or handle accordingly

        # Calculate subtotal for each order_product
        order_product.sub_total = discount_amount * quantity
        sub_total += order_product.sub_total  # Add to total subtotal

    # Calculate tax and grand total
    tax_rate = Decimal('0.02')  # Use Decimal for tax rate
    tax = sub_total * tax_rate  # Calculate tax
    grand_total = sub_total + tax  # Grand total is subtotal plus tax

    # Prepare context for rendering the payment page
    context = {
        'order': order,
        'payment': payment,
        'order_products': order_products,
        'tax': tax,
        'grand_total': grand_total,
        'sub_total': sub_total,
    }

    # Check if the form is submitted with a payment method
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        order.payment_method = payment_method  # Save payment method

        # Handle cash on delivery
        if payment_method == 'cash_on_delivery':
            order.cash_on_delivery = True  # Set cash on delivery
            order.is_ordered = True  # Mark the order as completed
            order.save()  # Save the order

            # Redirect to the dashboard or a confirmation page
            return redirect('dashboard')

        # For other payment methods, add logic if needed

    return render(request, 'orders/payments.html', context)


# def Payments(request, order_id, quantity=0):  ===> backup
#     # Fetch the order for the current user
#     order = get_object_or_404(Order, id=order_id, user=request.user)
#     payment = order.payment if order.is_ordered else None

#     # Fetch OrderProduct instances related to the order
#     order_products = OrderProduct.objects.filter(order=order)
#     sub_total = Decimal('0.00')  # Initialize total subtotal as Decimal

#     for order_product in order_products:
#         discount_amount = Decimal(order_product.discount_amount)  # Ensure it's Decimal
#         quantity = Decimal(order_product.quantity)  # Ensure quantity is Decimal
#         print(f"(order_product.quantity)")
#         order_product.sub_total = discount_amount * quantity  # Calculate subtotal for each order_product
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
#         'grand_total': grand_total,
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


# class CreatePaymentView(View):
#     def get(self, request, order_id):
#         order = get_object_or_404(Order, id=order_id)

#         # Build success and cancel URLs
#         success_url = request.build_absolute_uri(reverse('payment_success'))
#         cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
       
#         logger.debug(f"Success URL: {success_url}")
#         logger.debug(f"Cancel URL: {cancel_url}")
#         logging.debug(f"Success URL: {success_url}")

#         return render(request, 'orders/payment_form.html', {
#             'success_url': success_url,
#             'cancel_url': cancel_url,
#             'amount': order.order_total,
#             'cus_name': f"{order.first_name} {order.last_name}",
#             'cus_email': order.email,
#             'order': order
#         })

#     def post(self, request, order_id):
#         order = get_object_or_404(Order, id=order_id)

#         # Prepare payload for payment API
#         success_url = request.build_absolute_uri(reverse('payment_success'))
#         cancel_url = request.build_absolute_uri(reverse('payment_cancel'))
#         print(f"success_url",success_url)
#         payload = {
#             "cus_name": f"{order.first_name} {order.last_name}",
#             "cus_email": order.email,
#             "amount": str(order.order_total),
#             "success_url": success_url,
#             "cancel_url": cancel_url,
#             "webhook_url": "https://yourdomain.com/webhook",
#             "meta_data": json.dumps({"phone": order.phone})
#         }

#         logger.debug(f"Payload for payment creation: {payload}")

#         headers = {
#             'API-KEY': settings.IT_PAY_BD_API_KEY,
#             'Content-Type': 'application/json'
#         }

#         try:
#             response = requests.post(
#                 "https://pay.itpaybd.xyz/api/payment/create",
#                 headers=headers,
#                 json=payload
#             )
#             response_data = response.json()
#             logger.debug(f"Payment gateway response: {response_data}")

#             if response.ok and "payment_url" in response_data:
#                 payment_url = response_data.get("payment_url")
#                 transaction_id = response_data.get("transactionId")

#                 payment_method = request.POST.get('paymentMethod', 'Unknown')
#                 amount_paid = request.POST.get('paymentAmount', '0')
#                 status = request.POST.get('status', '').lower()

#                 # Validate and save payment information
#                 try:
#                     amount_paid = float(amount_paid)  # Convert to float
#                     payment = Payment(
#                         payment_id=transaction_id,
#                         payment_method=payment_method,
#                         amount_paid=amount_paid,
#                         status=status
#                     )
#                     payment.save()  # Save the payment record
#                     logger.info(f"Payment record saved: {payment}")
#                 except Exception as e:
#                     logger.error(f"Error saving payment record: {str(e)}")
#                     return JsonResponse({"status": "error", "message": "Failed to save payment record."})

#                 return JsonResponse({
#                     "status": 1,
#                     "payment_url": payment_url,
#                     "message": "Payment link created successfully."
#                 })
#             else:
#                 return JsonResponse({
#                     "status": "error",
#                     "message": response_data.get("message", "Payment gateway error.")
#                 })

#         except Exception as e:
#             logger.error(f"Error communicating with payment gateway: {str(e)}")
#             return JsonResponse({
#                 "status": "error",
#                 "message": "An error occurred while processing your payment."
#             })

class CreatePaymentView(View):
    def get(self, request, order_id):
        
        order = get_object_or_404(Order, id=order_id)
        
        
        success_url = request.build_absolute_uri(reverse('payment_success'))
        cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

        logger.debug(f"Success URL: {success_url}")
        logger.debug(f"Cancel URL: {cancel_url}")

        return render(request, 'orders/payment_form.html', {
            'success_url': success_url,
            'cancel_url': cancel_url,
            'amount': order.order_total,
            'cus_name': f"{order.first_name} {order.last_name}",
            'cus_email': order.email,
            'order': order
        })

    def post(self, request, order_id):
        user = request.user
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

        logger.debug(f"Payload for payment creation: {payload}")

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
            logger.debug(f"Payment gateway response: {response_data}")
               # Extract parameters from the query string
            payment_method = request.GET.get('paymentMethod')
            transaction_id = request.GET.get('transactionId')
            payment_amount = request.GET.get('paymentAmount')
            payment_fee = request.GET.get('paymentFee')
            status = request.GET.get('status')
            # Create a new Payment record
            payment = Payment(
                user=user,
                payment_id=transaction_id,
                payment_method=payment_method,
                amount_paid=payment_amount,  # Ensure it's converted to float
                status=status,
                # payment_fee = str(payment_fee)
            )
            payment.save()
            # # Save the payment record
            # try:
            #     payment.save()
            #     return JsonResponse({"status": "success", "message": "Payment record saved."})
            # except Exception as e:
            #     return JsonResponse({"status": "error", "message": str(e)})

            

            if response.ok and "payment_url" in response_data:
                payment_url = response_data.get("payment_url")
                # transaction_id = response_data.get("transaction_id")  # Updated key for transaction ID

                # # Create a Payment record
                # payment = Payment(
                #     user = request.user,
                #     payment_id=transaction_id,
                #     payment_method='Unknown',  # Set a default or handle it based on your business logic
                #     amount_paid=float(order.order_total),  # Assuming amount is already in float format
                #     status='PENDING'  # Set initial status as PENDING
                # )
                # payment.save()  # Save the payment record
                # logger.info(f"Payment record saved: {payment}")

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
            
# class PaymentSuccessView(View):
#     def get(self, request):
#         # Extract parameters from the query string
#         payment_method = request.GET.get('paymentMethod')
#         transaction_id = request.GET.get('transactionId')
#         payment_amount = request.GET.get('paymentAmount')
#         payment_fee = request.GET.get('paymentFee')
#         status = request.GET.get('status')

#         # Log the received data for debugging
#         print(f"Received payment data: {payment_method}, {transaction_id}, {payment_amount}, {payment_fee}, {status}")

#         # Assuming you have a user related to this payment (you might want to fetch it based on your logic)
#         user = get_object_or_404(User, email='admin@gmail.com')  # Adjust to find the correct user

#         # Create a new Payment record
#         payment = Payment(
#             user=user,
#             payment_id=transaction_id,
#             payment_method=payment_method,
#             amount_paid=float(payment_amount),  # Ensure it's converted to float
#             status=status
#         )

#         # Save the payment record
#         try:
#             payment.save()
#             return JsonResponse({"status": "success", "message": "Payment record saved."})
#         except Exception as e:
#             return JsonResponse({"status": "error", "message": str(e)})




class SuccessView(View):
    def get(self, request):
        transaction_id = request.GET.get('transactionId')
        payment_method = request.GET.get('paymentMethod', 'Unknown')
        amount = request.GET.get('paymentAmount')
        status = request.GET.get('status', '').lower()

        if not transaction_id:
            logger.error("Transaction ID is missing.")
            return render(request, 'orders/cancel.html', {
                'message': "Transaction ID is required."
            })
            

        verification_response = self.verify_payment(transaction_id)

        if status == "completed" and verification_response.get("status") == "COMPLETED":
            logger.info(f"Payment verified successfully for transaction ID: {transaction_id}")
            return render(request, 'orders/success.html', {
                'transaction_id': transaction_id,
                'payment_method': payment_method,
                'amount': amount,
                'status': "Success"
            })
        else:
            logger.error(f"Payment verification failed for transaction ID: {transaction_id}. Status: {status}, Verification Response: {verification_response}")
            return render(request, 'orders/cancel.html', {
                'message': f"Payment failed or verification unsuccessful for transaction ID: {transaction_id}."
            })

    def verify_payment(self, transaction_id):
        # Simulate verification logic; replace with actual implementation.
        
        
        valid_transaction_ids = ["N1P5LZ387234", "VALID_TRANSACTION_ID"]
        
        if transaction_id in valid_transaction_ids:
            return {"status": "COMPLETED"}
        
        return {"status": "FAILED"}


def payment_cancel(request):
    return HttpResponse


def generate_invoice(request, order_id):
    # Get the order using the order_id
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Ensure user ownership
    order_products = OrderProduct.objects.filter(order=order).select_related('product')

    # Create a context for the template
    context = {
        'order': order,
        'order_products': order_products,
        'request': request,  # Include the request object for absolute URLs
    }

    # Render the template to a string for PDF generation
    html = render_to_string('orders/invoice.html', context)

    # Create a PDF response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'

    # Generate PDF
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')

    return response

