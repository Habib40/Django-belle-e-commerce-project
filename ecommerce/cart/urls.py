from django.urls import path
from .import views

urlpatterns = [
    
    path('',views.CartPage,name='carts'),
    path('add_cart/<int:product_id>/', views.Add_to_Cart, name='addToCart'),
    path('minus_cart/<int:product_id>/<int:cart_item_id>/', views.Minus_cart, name='minus_cart'),
    path('remove_cart/<int:product_id>/', views.Remove_cart, name='remove_cart'),
]