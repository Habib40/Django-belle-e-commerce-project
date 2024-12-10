from django.urls import path
from django.contrib import admin
from .import views

urlpatterns = [
    path('bulk-create-order/', views.bulk_create_order,name='order'),
   
    
]