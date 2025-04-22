from .import views
from django.urls import path

urlpatterns =[
    
    path('place_order',views.PlaceOrder,name='place_order'),
    path('payments/<int:order_id>/',views.Payments,name='payments'),
    # path('payment/', views.payment_form, name='payment_form'),
    path('create-payment/<int:order_id>/', views.CreatePaymentView.as_view(), name='create_payment'),
    # path('success/', views.PaymentSuccessView.as_view(), name='payment_success'),
    path('success/', views.SuccessView.as_view(), name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice'),
    path('order_success/<int:order_id>/', views.order_success, name='order_success'),
]
