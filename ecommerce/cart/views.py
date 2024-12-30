from django.shortcuts import render,render,redirect ,HttpResponse,get_object_or_404
from shop.models import Product,ProductColor
from.models import Cart,CartItem
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import JsonResponse
import json
import uuid
from django.contrib.auth.decorators import login_required
import logging

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

def minus_cart(request, product_id):
    if request.method == 'POST':
        current_user = request.user

        if current_user.is_authenticated:
            print("Authenticated user detected.")
            try:
                cart = Cart.objects.get(user=current_user)
                cart_item = get_object_or_404(CartItem, product__id=product_id, cart=cart)
                print(f"Current item quantity: {cart_item.quantity}")

                if cart_item.quantity > 1:
                    cart_item.quantity -= 1  # Decrease the quantity
                    cart_item.save()  # Save changes
                    messages.success(request, "Item quantity decreased.")
                else:
                    cart_item.delete()  # Remove item if quantity is 0
                    messages.success(request, "Item removed from cart.")
                
                return JsonResponse({'status': 'success', 'new_quantity': cart_item.quantity})

            except Cart.DoesNotExist:
                messages.error(request, "Cart not found.")
                print("Cart does not exist.")
                return JsonResponse({'status': 'error', 'message': "Cart not found."}, status=404)
        else:
            print("Unauthenticated user detected.")
            if 'cart_items' in request.session:
                session_cart_items = request.session['cart_items']
                for item in session_cart_items:
                    if item['product_id'] == product_id:
                        print(f"Found item in session cart: {item}")
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
                return JsonResponse({'status': 'success', 'new_quantity': item['quantity'] if item['quantity'] > 0 else 0})
            else:
                messages.error(request, "You need to be logged in to modify the cart.")
                return JsonResponse({'status': 'error', 'message': "You need to be logged in."}, status=403)

    return JsonResponse({'status': 'error', 'message': "Invalid request method."}, status=400)
    

def Remove_cart(request, product_id):
    current_user = request.user

    if current_user.is_authenticated:
        try:
            cart = Cart.objects.get(user=current_user)
            # Find CartItem by product_id
            cart_item = get_object_or_404(CartItem, product__id=product_id, cart=cart)
            cart_item.delete()  # Remove the cart item
        except Cart.DoesNotExist:
            pass  # Handle case where cart does not exist
    else:
        if 'cart_items' in request.session:
            session_cart_items = request.session['cart_items']
            session_cart_items = [item for item in session_cart_items if item['product_id'] != product_id]
            request.session['cart_items'] = session_cart_items  # Update the session

    return redirect('carts')


def CartPage(request, total=0, quantity=0, cart_items=None):
    # Initialize totals
    total = 0
    quantity = 0
    tax = 0  # Initialize tax if needed
    grand_total = 0  # Initialize grand total if needed
    current_user = request.user

    # Initialize cart_items as an empty list
    cart_items = []

    if current_user.is_authenticated:
        # Retrieve the user's cart
        try:
            cart = Cart.objects.get(user=current_user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at')
        except Cart.DoesNotExist:
            cart_items = []  # No cart found for the user
    else:
        # For unauthenticated users, retrieve the cart using the session cart ID
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id).first()

        if cart:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at')

        # Check for items stored in the session
        if 'cart_items' in request.session:
            session_cart_items = request.session['cart_items']
            for item in session_cart_items:
                # Retrieve the product object to construct CartItem
                product = get_object_or_404(Product, id=item['product_id'])
                # Create a temporary dictionary to hold cart item information
                temp_cart_item = {
                    'product': product,
                    'quantity': item['quantity'],
                    'color': item['color'],
                    'size': item['size'],
                    'sub_total': product.discount_amount * item['quantity'],  # Calculate subtotal
                }
                cart_items.append(temp_cart_item)  # Append the temporary dictionary

    # Calculate total, quantity, tax, and grand total
    for cart_item in cart_items:
        # Ensure cart_item is a dictionary when coming from session
        if isinstance(cart_item, dict):
            item_total = cart_item['sub_total']  # Use pre-calculated subtotal
            quantity += cart_item['quantity']
        else:
            item_total = cart_item.product.discount_amount * cart_item.quantity  # Calculate total for the item
            quantity += cart_item.quantity

        total += item_total

    # Example tax calculation (2% of total)
    tax = (2 * total) / 100
    grand_total = tax + total

    # Prepare context for rendering
    context = {
        'cart_items': cart_items,
        'total': total,
        'grand_total': grand_total,
        'tax': tax,
        'cart_empty': not cart_items  # Flag for empty cart
    }

    return render(request, 'cart.html', context)


@login_required(login_url='login')    
def Checkout(request):
    # Initialize totals
    total = 0
    quantity = 0
    tax = 0
    grand_total = 0
    current_user = request.user
    cart_items = []

    try:
        if current_user.is_authenticated:
            cart_items = CartItem.objects.filter(user=current_user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            # Calculate subtotal for the current cart item
            sub_total = cart_item.product.discount_amount * cart_item.quantity
            total += sub_total
            quantity += cart_item.quantity

        # Calculate tax and grand total
        tax = (2 * total) / 100  # Assuming a 2% tax rate
        grand_total = total + tax

    except ObjectDoesNotExist:
        cart_items = []

    return render(request, 'accounts/checkout.html', {
        'cart_items': cart_items,
        'total': total,
        'quantity': quantity,
        'tax': tax,
        'grand_total': grand_total,
    })