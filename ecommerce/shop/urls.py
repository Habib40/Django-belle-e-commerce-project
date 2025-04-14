from django.urls import path
from .import views

# Import your custom 404 view
from django.conf.urls import handler404
from .views import custom_404_view



urlpatterns = [
    
    
    path('',views.OureStore,name='store'),
    path('category/<slug:category_slug>/', views.OureStore, name='store_by_category'),  # For category-specific products
    path('load/', views.LoadProducts),
    path('details/<slug:category_slug>/<slug:product_slug>/', views.ProductDetail, name='productDetails'),
    path('myWishList/', views.WishListView, name='myWishList'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('search/',views.Search,name='search')
    
    
]
# Set the custom 404 handler
handler404 = custom_404_view