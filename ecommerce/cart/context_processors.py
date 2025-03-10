from .models import Cart, CartItem
from .views import _cart_id
from shop.models import Product
from django.shortcuts import get_object_or_404

def cart_context(request, cart_item_id=None):
    total = 0
    cart_items = []  # Initialize as an empty list
    items_count = 0

    if request.user.is_authenticated:
        # For authenticated users, get their cart
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = list(CartItem.objects.filter(cart=cart, is_active=True))  # Convert QuerySet to list
    else:
        # For unauthenticated users, use the session-based cart
        cart_id = _cart_id(request)
        cart = Cart.objects.filter(cart_id=cart_id).first()

        if cart:
            cart_items = list(CartItem.objects.filter(cart=cart, is_active=True))  # Convert QuerySet to list

        # Include session-based cart items for unauthenticated users
        if 'cart_items' in request.session:
            for item in request.session['cart_items']:
                product = get_object_or_404(Product, id=item['product_id'])
                # Create a dict representation to hold necessary item details
                cart_items.append({
                    'product': product,
                    'color': item['color'],
                    'size': item['size'],
                    'quantity': item['quantity'],
                    'total': item['quantity'] * product.discount_amount  # Calculate total for display
                })

    # Calculate total and items count
    items_count = len(cart_items)  # Count of cart items

    # Calculate total dynamically
    total = sum(item['total'] for item in cart_items if isinstance(item, dict))  # For session items
    total += sum(item.quantity * item.product.discount_amount for item in cart_items if isinstance(item, CartItem))  # For CartItem instances

    # Tax and grand total calculations
    tax = (2 * total) / 100  # Example tax calculation
    grand_total = total + tax  # Grand total including tax

    return {
        'cart_items': cart_items,
        'total': total,
        'grand_total': grand_total,
        'tax': tax,
        'items_count': items_count,
    }
    

