from django.shortcuts import render,render,redirect ,HttpResponse,get_object_or_404
from shop.models import Product,ProductColor,WishList
from promotions.models import AppliedPromotion
from.models import Cart,CartItem
from promotions.models import Promotion
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

logger = logging.getLogger(__name__)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart
    
def Add_to_Cart(request, product_id):
    current_user = request.user
    cart = _cart_id(request)  # Get or create cart_id from session

    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        color = request.POST.get('color')
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))

        # Handle authenticated users
        if current_user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=current_user)

            # Create or update the CartItem
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                color=color,
                size=size,
                defaults={'quantity': quantity, 'user': current_user}
            )

            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            #  # Remove the item from the wishlist if it exists
             
            WishList.objects.filter(user=current_user, wish_product=product).delete()

            

        else:
            # Handle unauthenticated users
            if 'cart_items' not in request.session:
                request.session['cart_items'] = []

            # Check if the item already exists in the session cart
            item_exists = False
            for item in request.session['cart_items']:
                if item['product_id'] == product.id and item['color'] == color and item['size'] == size:
                    item['quantity'] += quantity
                    item_exists = True
                    break

            if not item_exists:
                request.session['cart_items'].append({
                    'product_id': product.id,
                    'color': color,
                    'size': size,
                    'quantity': quantity
                })

            request.session.modified = True  # Mark the session as modified
           

        return redirect('carts')
    else:
        return redirect('carts')
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import Cart, CartItem

# def minus_cart(request, product_id):
#     print("minus_cart function called with product_id:", product_id)
#     if request.method == 'POST':
#         current_user = request.user

#         if current_user.is_authenticated:
#             print("Authenticated user detected.")
#             try:
#                 cart = Cart.objects.get(user=current_user)
#                 cart_item = get_object_or_404(CartItem, product__id=product_id, cart=cart)
#                 print(f"Current item quantity: {cart_item.quantity}")

#                 if cart_item.quantity > 1:
#                     cart_item.quantity -= 1  # Decrease the quantity
#                     cart_item.save()  # Save changes
#                     print(f"Updated item quantity: {cart_item.quantity}")
#                     messages.success(request, "Item quantity decreased.")
#                     new_quantity = cart_item.quantity
#                 else:
#                     print("Quantity is 0, item will be deleted.")
#                     cart_item.delete()  # Remove item if quantity is 0
#                     messages.success(request, "Item removed from cart.")
#                     new_quantity = 0  # Set quantity to 0 after deletion
                
#                 # return JsonResponse({'status': 'success', 'new_quantity': new_quantity})
#                 return redirect('carts')

#             except Cart.DoesNotExist:
#                 messages.error(request, "Cart not found.")
#                 print("Cart does not exist.")
#                 return JsonResponse({'status': 'error', 'message': "Cart not found."}, status=404)
#             except Exception as e:
#                 print(f"Error occurred: {e}")
#                 messages.error(request, "An error occurred while updating the cart.")
#                 return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

#         else:
#             print("Unauthenticated user detected.")
#             session_cart_items = request.session.get('cart_items', [])
#             item_found = False

#             for item in session_cart_items:
#                 if item['product_id'] == product_id:
#                     print(f"Found item in session cart: {item}")
#                     if item['quantity'] > 1:
#                         item['quantity'] -= 1  # Decrease the quantity
#                         messages.success(request, "Item quantity decreased.")
#                         new_quantity = item['quantity']
#                     else:
#                         print("Quantity is 0, item will be removed from session cart.")
#                         session_cart_items.remove(item)  # Remove item if quantity is 0
#                         messages.success(request, "Item removed from cart.")
#                         new_quantity = 0  # Set quantity to 0 after deletion
#                     item_found = True
#                     break

#             if not item_found:
#                 messages.error(request, "Item not found in session cart.")
#                 return JsonResponse({'status': 'error', 'message': "Item not found in session cart."}, status=404)

#             # Update session cart items
#             request.session['cart_items'] = session_cart_items
#             request.session.modified = True  # Mark session as modified
#             print(f"Updated session cart items: {session_cart_items}")
#             # return JsonResponse({'status': 'success', 'new_quantity': new_quantity})
#             return redirect('carts')

#     print("Minus Cart is called")
#     return redirect('checkout')

# def minus_cart(request, product_id):
#     if request.method == 'POST':
#         current_user = request.user

#         if current_user.is_authenticated:
#             print("Authenticated user detected.")
#             try:
#                 cart = Cart.objects.get(user=current_user)
#                 cart_item = get_object_or_404(CartItem, product__id=product_id, cart=cart)
#                 print(f"Current item quantity: {cart_item.quantity}")

#                 if cart_item.quantity > 1:
#                     cart_item.quantity -= 1  # Decrease the quantity
#                     cart_item.save()  # Save changes
#                     messages.success(request, "Item quantity decreased.")
#                 else:
#                     cart_item.delete()  # Remove item if quantity is 0
#                     messages.success(request, "Item removed from cart.")
                
#                 return JsonResponse({'status': 'success', 'new_quantity': cart_item.quantity})

#             except Cart.DoesNotExist:
#                 messages.error(request, "Cart not found.")
#                 print("Cart does not exist.")
#                 return JsonResponse({'status': 'error', 'message': "Cart not found."}, status=404)
#         else:
#             print("Unauthenticated user detected.")
#             if 'cart_items' in request.session:
#                 session_cart_items = request.session['cart_items']
#                 for item in session_cart_items:
#                     if item['product_id'] == product_id:
#                         print(f"Found item in session cart: {item}")
#                         if item['quantity'] > 1:
#                             item['quantity'] -= 1  # Decrease the quantity
#                             messages.success(request, "Item quantity decreased.")
#                         else:
#                             session_cart_items.remove(item)  # Remove item if quantity is 0
#                             messages.success(request, "Item removed from cart.")
#                         break
#                 else:
#                     messages.error(request, "Item not found in session cart.")

#                 request.session['cart_items'] = session_cart_items  # Update the session
#             else:
#                 messages.error(request, "You need to be logged in to modify the cart.")
#     print("Minus Cart is called")
#     return redirect('carts')


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


def calculate_totals(cart_items):
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

    return total, quantity

def handle_promo_code(request, current_user, total):
    discount = Decimal(0)
    promo_code = request.POST.get('promo_code')

    if promo_code:
        try:
            promotion = Promotion.objects.get(code=promo_code)
            discount = (promotion.discount_percentage / Decimal(100)) * total
            discount = min(discount, total)  # Prevent discount > total

            messages.success(request, "Promo code applied successfully.")

            if current_user.is_authenticated:
                AppliedPromotion.objects.update_or_create(
                    user=current_user,
                    promo_code=promo_code,
                    defaults={'discount': discount}
                )
                # Store in session for authenticated users as well
                request.session['discount'] = float(discount)
                request.session['promo_code'] = promo_code
            else:
                request.session['discount'] = float(discount)
                request.session['promo_code'] = promo_code

        except Promotion.DoesNotExist:
            messages.error(request, "Invalid promo code. Please try again.")

    return discount

def CartPage(request, total=0, quantity=0, cart_items=None):
    print("CartPage is Called")
    current_user = request.user
    tax = Decimal(0)
    grand_total = Decimal(0)
    discount = Decimal(0)

    # Retrieve the user's cart
    if current_user.is_authenticated:
        cart = Cart.objects.filter(user=current_user).first()
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at') if cart else []
    else:
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id).first()
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at') if cart else []

        # Check for items in session
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

    total, quantity = calculate_totals(cart_items)

    # Example tax calculation (2% of total)
    tax = (Decimal(2) * total) / Decimal(100)
    grand_total = total + tax

    # Handle promo code application
    if request.method == 'POST':
        discount = handle_promo_code(request, current_user, total)
        grand_total = total + tax - discount
    else:
        # Check if there's a discount in the session for unauthenticated users
        if not current_user.is_authenticated and 'discount' in request.session:
            discount = Decimal(request.session['discount'])
            grand_total = total + tax - discount
        # For authenticated users, check for applied promotions
        elif current_user.is_authenticated:
            applied_promos = AppliedPromotion.objects.filter(user=current_user)
            if applied_promos.exists():
                last_promo = applied_promos.last()
                discount = last_promo.discount
                grand_total = total + tax - discount

    # Clear session discount if the cart is empty
    if not cart_items:
        request.session.pop('discount', None)
        request.session.pop('promo_code', None)

    # Prepare context for rendering
    context = {
        'cart_items': cart_items,
        'total': total,
        'grand_total': grand_total,
        'tax': tax,
        'cart_empty': not cart_items,
        'discount': round(float(discount), 4),
    }
    return render(request, 'cart.html', context)



@login_required(login_url='login')
def Checkout(request):
    # Initialize totals
    total = Decimal(0)
    quantity = 0
    tax_rate = Decimal(0.02)  # 2% tax
    grand_total = Decimal(0)
    discount = Decimal(0)

    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user, is_active=True)

    # Calculate total, quantity, and subtotal for each item
    for cart_item in cart_items:
        sub_total = cart_item.product.discount_amount * cart_item.quantity
        total += sub_total
        quantity += cart_item.quantity

    # Retrieve discount from session
    discount = Decimal(request.session.get('discount', 0))  # Default to 0 if not set

    # Calculate Total After Discount
    total_after_discount = total - discount

    # Calculate tax
    tax = total_after_discount * tax_rate

    # Grand Total Calculation
    grand_total = total_after_discount + tax

    # Ensure grand total does not go negative
    if grand_total < 0:
        grand_total = Decimal(0)

    # Create an Order instance and save it
    if request.method == 'POST':
        order = Order.objects.create(
            user=current_user,
            total_price=grand_total,
            original_price=total,
            tax=tax,
            discount=discount
        )

        # Add items to the order
        for cart_item in cart_items:
            OrderProduct.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.discount_amount
            )

        # Clear the cart or mark items as purchased
        cart_items.delete()  # Adjust as necessary for your application logic

        # Clear the session discount after order creation
        request.session.pop('discount', None)
        request.session.pop('promo_code', None)

        # Redirect to the order success page
        return redirect('order_success')

    # Prepare the context
    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
        'discount': round(float(discount), 4),  # Optional: Include discount in context
    }

    return render(request, 'accounts/checkout.html', context)

def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user, is_active=True)
        cart_item.delete()  # Remove the item from the cart

        # Optionally, you can add a success message here

    return redirect('checkout')  # Redirect back to the checkout page
