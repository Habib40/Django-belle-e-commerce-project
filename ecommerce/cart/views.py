from django.shortcuts import render,render,redirect ,HttpResponse,get_object_or_404
from shop.models import Product,ProductColor
from.models import Cart,CartItem
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.http import JsonResponse
import json
# Create your views here.

# Creating a private function for getting session_key
def _cart_id(request):
    # Get the session key for the cart
    cart = request.session.session_key
    
    # If there is no cart session key, create a new session
    if not cart:
        cart = request.session.create()
    
    # Return the cart session key
    return cart

def Add_to_Cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # Get color, size, and quantity from the request
        color = request.POST.get('color')
        size = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided

        # Get or create the cart
       
        cart, created = Cart.objects.get_or_create(cart_id =_cart_id(request))

        # Ensure that the combination of color and size is unique
        cart_item, created = CartItem.objects.get_or_create(
            
            cart=cart,
            product=product,
            color=color,
            size=size,
        )

        if created:
            # Set the quantity for a new item
            cart_item.quantity = quantity
        else:
            # Increment the quantity if the item already exists
            cart_item.quantity += quantity
            # return redirect('error_page')  # Modify this to your error handling
        
            cart_item.save()  # Save the CartItem
        
        return redirect('carts')  # Redirect to the cart view
    else:
        return redirect('carts')  # Redirect for GET requests # Pass product ID to redire



import logging

logger = logging.getLogger(__name__)

def Minus_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, cart_id=_cart_id(request))

    try:
        # Get the specific cart item
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        print(f"Current quantity for item ID {cart_item_id}: {cart_item.quantity}")

        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            print(f"Decreased quantity for item ID {cart_item_id}: {cart_item.quantity}")
        else:
            cart_item.delete()
            print(f"Deleted item ID {cart_item_id} from cart.")

        return redirect('carts')
    
    except CartItem.DoesNotExist:
        print(f"CartItem with ID {cart_item_id} not found.")
        return redirect('carts')
    except Exception as e:
        print(f"An error occurred: {e}")
        return redirect('carts')

def Remove_cart(request, product_id):
    if request.method == 'POST':  # Ensure this only handles POST requests
        color = request.POST.get('color', None)  # Get color; default to None
        size = request.POST.get('size', None)    # Get size; default to None

        # Get the cart using the session cart_id
        cart = get_object_or_404(Cart, cart_id=_cart_id(request))
        
        # Get the product to be removed
        product = get_object_or_404(Product, id=product_id)

        # Try to find the CartItem based on product and cart
        try:
            if color is not None and size is not None:
                # If both color and size are specified
                cart_item = CartItem.objects.get(product=product, cart=cart, color=color, size=size)
            else:
                # If color or size is None, retrieve the CartItem without those filters
                cart_item = CartItem.objects.get(product=product, cart=cart, color=color, size=size)

            cart_item.delete()  # Remove the item from the cart
        except CartItem.DoesNotExist:
            # Optional: Log the error or handle the case where the item does not exist
            print(f"CartItem not found for product_id: {product_id}, color: {color}, size: {size}")

        return redirect('carts')  # Redirect to the cart view
    return redirect('carts')  # Redirect for non-POST requests

def CartPage(request, total=0, quantity=0, cart_items=None):
    tax = 0
    grand_total = 0
    
    # Attempt to get the cart associated with the session
    cart_id = _cart_id(request)
    cart = Cart.objects.filter(cart_id=cart_id).first()  # Get the first matching cart

    if cart:
        cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('-created_at')
    else:
        cart_items = []  # No cart found, initialize as empty list

    # Calculate total, quantity, tax, and grand total
    for cart_item in cart_items:
        total += (cart_item.product.discount_amount * cart_item.quantity)
        cart_item.total = cart_item.product.discount_amount * cart_item.quantity
        quantity += cart_item.quantity

    tax = (2 * total) / 100
    grand_total = tax + total
    
    
    context={
        'cart_items':cart_items,
        'total':total,
        'grand_total':grand_total,
        'tax':tax
    }
    return render(request ,'cart.html',context)