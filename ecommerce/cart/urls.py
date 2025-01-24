from django.urls import path
from .import views

urlpatterns = [
    
    path('',views.CartPage,name='carts'),
    path('add_cart/<int:product_id>/', views.Add_to_Cart, name='addToCart'),
    path('carts/minus/<int:product_id>/', views.minus_cart, name='minus_cart'),
    # path('remove_cart/<int:product_id>/', views.Remove_cart, name='remove_cart'),
    path('remove_cart/<int:product_id>/<str:color>/<str:size>/', views.Remove_cart, name='remove_cart'),
    # checkout
    path('checkout/',views.Checkout,name='checkout')
]