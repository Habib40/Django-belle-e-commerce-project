from .models import Cart, CartItem
from .views import _cart_id

def cart_context(request, cart_item_id=None):
    cart_id = _cart_id(request)  # Ensure this function is defined
    cart = Cart.objects.filter(cart_id=cart_id).first()  # Use cart_id variable

    total = 0
    cart_items = []
    items_count = 0  # Initialize items_count

    if cart:
        # If cart_item_id is provided, filter by it; otherwise, get all active items
        if cart_item_id:
            cart_items = CartItem.objects.filter(cart=cart, id=cart_item_id, is_active=True)
        else:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        items_count = cart_items.count()  # Count of cart items
        total = sum(item.product.discount_amount * item.quantity for item in cart_items)  # Total cost calculation
        
        # Add subtotal to each cart item
        for item in cart_items:
            item.total = item.product.discount_amount * item.quantity  # Calculate subtotal for each item

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