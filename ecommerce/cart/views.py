from django.shortcuts import render,render,redirect ,HttpResponse,get_object_or_404
from shop.models import Product,ProductColor,WishList
from promotions.models import AppliedPromotion
from.models import Cart,CartItem
from promotions.models import Coupon
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import JsonResponse
import json
import uuid
from django.contrib.auth.decorators import login_required
import logging
from decimal import Decimal
from order.models import OrderProduct,Order
from order.forms import OrderForm
import datetime

logger = logging.getLogger(__name__)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
def get_or_create_cart(request):
    current_user = request.user
    cart_id = _cart_id(request)
    
    if current_user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=current_user)
    else:
        cart, created = Cart.objects.get_or_create(
            cart_id=cart_id,
            defaults={'is_guest': True}
        )
    
    return cart
def Add_to_Cart(request, product_id):
    current_user = request.user
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        color = request.POST.get('color')
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        
        cart = get_or_create_cart(request)
        
        # Check if item already exists in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            color=color,
            size=size,
            defaults={
                'quantity': quantity,
                'user': current_user if current_user.is_authenticated else None
            }
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        if current_user.is_authenticated:
            # Remove from wishlist if exists
            WishList.objects.filter(user=current_user, wish_product=product).delete()
        
        return redirect('carts')
    
    return redirect('carts')
# def Add_to_Cart(request, product_id):
#     current_user = request.user
#     cart = _cart_id(request)  # Get or create cart_id from session

#     if request.method == 'POST':
#         product = get_object_or_404(Product, id=product_id)
#         color = request.POST.get('color')
#         size = request.POST.get('size')
#         quantity = int(request.POST.get('quantity', 1))

#         # Handle authenticated users
#         if current_user.is_authenticated:
#             cart, created = Cart.objects.get_or_create(user=current_user)

#             # Create or update the CartItem
#             cart_item, created = CartItem.objects.get_or_create(
#                 cart=cart,
#                 product=product,
#                 color=color,
#                 size=size,
#                 defaults={'quantity': quantity, 'user': current_user}
#             )

#             if not created:
#                 cart_item.quantity += quantity
#                 cart_item.save()
#             #  # Remove the item from the wishlist if it exists
             
#             WishList.objects.filter(user=current_user, wish_product=product).delete()
#         else:
#             # Handle unauthenticated users
#             if 'cart_items' not in request.session:
#                 request.session['cart_items'] = []

#             # Check if the item already exists in the session cart
#             item_exists = False
#             for item in request.session['cart_items']:
#                 if item['product_id'] == product.id and item['color'] == color and item['size'] == size:
#                     item['quantity'] += quantity
#                     item_exists = True
#                     break

#             if not item_exists:
#                 request.session['cart_items'].append({
#                     'product_id': product.id,
#                     'color': color,
#                     'size': size,
#                     'quantity': quantity
#                 })

#             request.session.modified = True  # Mark the session as modified
           

#         return redirect('carts')
#     else:
#         return redirect('carts')

def minus_cart(request, product_id, color, size):
    if request.method == 'POST':
        current_user = request.user

        if current_user.is_authenticated:
            try:
                cart = Cart.objects.get(user=current_user)
                # Get the CartItem based on product_id, cart, color, and size
                cart_item = get_object_or_404(CartItem, 
                                               product__id=product_id,
                                               cart=cart,
                                               color=color, 
                                               size=size)

                if cart_item.quantity > 1:
                    cart_item.quantity -= 1  # Decrease the quantity
                    cart_item.save()  # Save changes
                    messages.success(request, "Item quantity decreased.")
                else:
                    cart_item.delete()  # Remove item if quantity is 0
                    messages.success(request, "Item removed from cart.")
                
                # return JsonResponse({'status': 'success', 'new_quantity': cart_item.quantity})
                return redirect('carts')

            except Cart.DoesNotExist:
                messages.error(request, "Cart not found.")
                return JsonResponse({'status': 'error', 'message': "Cart not found."}, status=404)

        else:
            # Handle session cart logic
            if 'cart_items' in request.session:
                session_cart_items = request.session['cart_items']
                for item in session_cart_items:
                    if (item['product_id'] == product_id and 
                        item['color'] == color and 
                        item['size'] == size):
                        if item['quantity'] > 1:
                            item['quantity'] -= 1  # Decrease the quantity
                            messages.success(request, "Item quantity decreased.")
                        else:
                            session_cart_items.remove(item)  # Remove item if quantity is 0
                            messages.success(request, "Item removed from cart.")
                        break
                else:
                    messages.error(request, "Item not found in session cart.")

                request.session['cart_items'] = session_cart_items  # Update the session
            else:
                messages.error(request, "You need to be logged in to modify the cart.")

    return redirect('carts')
    




def Remove_cart(request, product_id, color, size):
    current_user = request.user

    if current_user.is_authenticated:
        try:
            cart = Cart.objects.get(user=current_user)
            # Find the specific CartItem for the product with the specified color and size
            cart_items = CartItem.objects.filter(
                product__id=product_id,
                cart=cart,
                color=color,
                size=size
            )

            if cart_items.exists():
                # Delete all matching items
                cart_items.delete()
                print(f"Deleted {cart_items.count()} items with product ID: {product_id}, color: {color}, size: {size}")
            else:
                print("No matching items found in the cart.")

        except Cart.DoesNotExist:
            print("Cart does not exist for the user.")
        except Exception as e:
            print(f"Error occurred: {e}")
    else:
        # Handling session cart items
        if 'cart_items' in request.session:
            session_cart_items = request.session['cart_items']
            session_cart_items = [
                item for item in session_cart_items
                if item['product_id'] != product_id or item['color'] != color or item['size'] != size
            ]
            request.session['cart_items'] = session_cart_items  # Update the session
            print(f"Updated session cart. Remaining items: {len(request.session['cart_items'])}")

    return redirect('carts')


def calculate_totals(cart_items, coupon=None):
    total = Decimal(0)
    quantity = 0
    for cart_item in cart_items:
        if isinstance(cart_item, dict):
            item_total = cart_item['sub_total']
            quantity += cart_item['quantity']
        else:
            item_total = cart_item.product.discount_amount * cart_item.quantity
            quantity += cart_item.quantity
        total += item_total

    # Apply coupon discount
    if coupon:
        if coupon.discount:
            total -= (total * coupon.discount / 100)

    return total, quantity
def CartPage(request, total=0, quantity=0, cart_items=None):
    current_user = request.user
    tax = Decimal(0)
    grand_total = Decimal(0)
    discount = Decimal(0)

    # Retrieve the user's cart
    if current_user.is_authenticated:
        cart = Cart.objects.filter(user=current_user).first()
    else:
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id).first()

    # Initialize the cart_items list
    cart_items = []

    # Check if the cart exists and retrieve its items
    if cart:
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at')

    # Check for items in session (if applicable)
    if 'cart_items' in request.session:
        session_cart_items = request.session['cart_items']
        for item in session_cart_items:
            product = get_object_or_404(Product, id=item['product_id'])
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'color': item['color'],
                'size': item['size'],
                'sub_total': product.discount_amount * item['quantity'],
            })

    # Calculate totals from cart items
    total, quantity = calculate_totals(cart_items, cart.coupon if cart else None)
    # Calculate tax and grand total
    total_after_discount = total - discount
    tax = (Decimal(2) * total_after_discount) / Decimal(100)  # Calculate tax after discount
    grand_total = total_after_discount + tax  # Calculate grand total

    # Ensure consistent rounding
    grand_total = round(grand_total, 2)
   
    # Prepare context for rendering
    context = {
        'cart_items': cart_items,
        'total': round(total, 2),  # Ensure total is rounded consistently
        'grand_total': grand_total,
        'tax': round(tax, 2),
        'cart_empty': not cart_items,
        'cart': cart  # Include the cart in context for template access
    }
    
    return render(request, 'cart.html', context)
def Checkout(request):
    current_user = request.user
    is_guest = not current_user.is_authenticated
    
    if is_guest:
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id, is_guest=True).first()
        cart_items = CartItem.objects.filter(cart=cart, is_active=True) if cart else []
    else:
        cart = Cart.objects.filter(user=current_user).first()
        cart_items = CartItem.objects.filter(user=current_user, is_active=True)

    # if not cart_items.exists():
    #     messages.warning(request, "Your cart is empty.")
    #     return redirect('store')
    if (is_guest and not cart) or not cart_items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('store')

    total = Decimal(0)
    quantity = 0
    discount = Decimal(0)
    tax_rate = Decimal('0.02')  # 2% tax

    # Calculate total and quantity
    for item in cart_items:
        total += item.sub_total()
        quantity += item.quantity

    # Handle order creation
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Recalculate totals
            total = sum(item.sub_total() for item in cart_items)
            
            # Apply coupon if valid
            if cart and cart.coupon and cart.coupon.is_valid():
                coupon = cart.coupon
                discount = (total * coupon.discount / 100)
                coupon.used_count += 1
                coupon.save()
            else:
                coupon = None

            total_after_discount = total - discount
            tax = total_after_discount * tax_rate
            grand_total = total_after_discount + tax

            # Prevent negative total
            if grand_total < 0:
                grand_total = Decimal(0)

            # Create order
            order_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'address_line_1': form.cleaned_data['address_line_1'],
                'address_line_2': form.cleaned_data['address_line_2'],
                'country': form.cleaned_data['country'],
                'state': form.cleaned_data['state'],
                'city': form.cleaned_data['city'],
                'order_note': form.cleaned_data['order_note'],
                'order_total': grand_total,
                'tax': tax,
                'ip': request.META.get('REMOTE_ADDR'),
                'discount': discount,
                'coupon': coupon,
            }
            
            if not is_guest:
                order_data['user'] = current_user
            
            order = Order.objects.create(**order_data)
            order.order_number = f"{datetime.date.today():%Y%d%m}-{order.id}"
            order.save()

            # Create order products
            for item in cart_items:
                OrderProduct.objects.create(
                    order=order,
                    user=item.user,  # Could be None for guest
                    product=item.product,
                    quantity=item.quantity,
                    product_price=item.product.discount_amount,
                    color=item.color,
                    size=item.size
                )
            
            # Clear cart
            cart_items.delete()
            if cart:
                cart.coupon = None
                cart.save()

            # For guest users, clear the session cart
            if is_guest:
                if 'cart_id' in request.session:
                    del request.session['cart_id']

            return redirect('order_success')
        else:
            messages.error(request, 'Form errors. Please correct them.')

    # Calculate tax and grand total for display (GET request)
    if cart and cart.coupon and cart.coupon.is_valid():
        discount = (total * cart.coupon.discount / 100)
        total_after_discount = total - discount
    else:
        total_after_discount = total
        discount = Decimal(0)

    tax = total_after_discount * tax_rate
    grand_total = total_after_discount + tax

    # For guest checkout, we need to create a form
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
        'total': round(total, 2),
        'quantity': quantity,
        'tax': round(tax, 2),
        'grand_total': round(grand_total, 2),
        'discount': round(discount, 2),
        'is_guest': is_guest,
    }

    return render(request, 'accounts/checkout.html', context)

# @login_required(login_url='login')
# def Checkout(request):
#     current_user = request.user
#     cart = Cart.objects.filter(user=current_user).first()
#     cart_items = CartItem.objects.filter(user=current_user, is_active=True)

#     total = Decimal(0)
#     quantity = 0
#     discount = Decimal(0)
#     tax_rate = Decimal('0.02')  # 2% tax

#     # Calculate total and quantity
#     for item in cart_items:
#         sub_total = item.product.discount_amount * item.quantity
#         total += sub_total
#         quantity += item.quantity

#     # Handle order creation
#     if request.method == 'POST':
#         # Recalculate in POST to ensure consistency
#         total = Decimal(0)
#         for item in cart_items:
#             total += item.product.discount_amount * item.quantity

#         discount = Decimal(0)
#         coupon = None

#         # Apply coupon if valid
#         if cart and cart.coupon and cart.coupon.is_valid():
#             coupon = cart.coupon
#             discount = (total * coupon.discount / 100)
#             coupon.used_count += 1
#             coupon.save()

#         total_after_discount = total - discount
#         tax = total_after_discount * tax_rate
#         grand_total = total_after_discount + tax

#         # Prevent negative total
#         if grand_total < 0:
#             grand_total = Decimal(0)

#         # Save the order
#         order = Order.objects.create(
#             user=current_user,
#             order_total=grand_total,
#             tax=tax,
#             discount=discount,
#             coupon=coupon
#         )

#         # Save ordered products
#         for item in cart_items:
#             OrderProduct.objects.create(
#                 order=order,
#                 product=item.product,
#                 quantity=item.quantity,
#                 product_price=item.product.discount_amount
#             )
        
#         # Clear cart and coupon
#         cart_items.delete()
#         if cart:
#             cart.coupon = None
#             cart.save()

#         return redirect('order_success')

#     # Calculate tax and grand total for display (GET request)
#     if cart and cart.coupon and cart.coupon.is_valid():
#         discount = (total * cart.coupon.discount / 100)
#         total_after_discount = total - discount
#     else:
#         total_after_discount = total
#         discount = Decimal(0)

#     tax = total_after_discount * tax_rate
#     grand_total = total_after_discount + tax

#     context = {
#         'cart_items': cart_items,
#         'total': round(total, 2),
#         'quantity': quantity,
#         'tax': round(tax, 2),
#         'grand_total': round(grand_total, 2),
#         'discount': round(discount, 2),
#     }

#     return render(request, 'accounts/checkout.html', context)

def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user, is_active=True)
        cart_item.delete()  # Remove the item from the cart

        # Optionally, you can add a success message here

    return redirect('checkout')  # Redirect back to the checkout page
