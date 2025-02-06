from django.db import models
from account.models import Account
from shop.models import Product,ProductColor
import uuid
from django.conf import settings



class Cart(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
    cart_id = models.CharField(max_length=250,blank=True,default=str(uuid.uuid4()))
    date_added = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.cart_id

    
class CartItem(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True) 
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # New fields for color and size using color and size fields instead of variations
    color = models.CharField(max_length=50, null=True,blank=True)  
    size = models.CharField(max_length=50, null=True,blank=True)   
    quantity = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('product', 'color', 'size', 'cart')  # Prevent duplicates based on color and size
    
    
    def sub_total(self):
        return self.product.discount_amount * self.quantity
    
    def __str__(self):
        return f"Cart item for {self.product.title}"
    
    
