from .import views
from django.urls import path

urlpatterns =[
    
    path('place_order',views.PlaceOrder,name='place_order'),
    path('payments/<int:order_id>/',views.Payments,name='payments')
   
]
