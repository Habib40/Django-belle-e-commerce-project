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
    total, quantity = calculate_totals(cart_items)
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
        # 'discount': round(float(discount), 2),
        'cart': cart  # Include the cart in context for template access
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
    # Calculate Total After Discount
    total_after_discount = total - discount
    # Calculate tax
    tax = (total_after_discount * tax_rate)  # Calculate 2% tax
    # Grand Total Calculation
    grand_total = total_after_discount + tax

    # Ensure grand total does not go negative
    if grand_total < 0:
        grand_total = Decimal(0)

    # Handle order submission
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
        return redirect('order_success')

    context = {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': round(tax, 2),  # Round tax for display consistency
        'grand_total': round(grand_total, 2),  # Round to two decimal places
        'discount': round(float(discount), 2),  # Optional: Include discount in context
    }

    return render(request, 'accounts/checkout.html', context)

def remove_cart_item(request, item_id):
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user, is_active=True)
        cart_item.delete()  # Remove the item from the cart

        # Optionally, you can add a success message here

    return redirect('checkout')  # Redirect back to the checkout page
