# myapp/context_processors.py

# myapp/context_processors.py

from .models import WishList  # Adjust based on your app structure

def wishlist_items(request):
    count = 0
    if request.user.is_authenticated:
        wishlist_items = WishList.objects.filter(user=request.user)
        count = wishlist_items.count()
        
    return {
        'wishlist_count': count,  # Use 'wishlist_count' for the count
    }