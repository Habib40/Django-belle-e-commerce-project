from django.urls import path
from .import views

# Import your custom 404 view
from django.conf.urls import handler404
from .views import custom_404_view



urlpatterns = [
    
    path('',views.Index,name='index'),
    path('load/', views.LoadProducts),
    path('details/<int:product_id>/<slug:product_slug>/',views.ProductDetail,name='productDtails'),
    
]
# Set the custom 404 handler
handler404 = custom_404_view