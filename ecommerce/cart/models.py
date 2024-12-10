from django.db import models
from shop.models import Product,ProductColor




class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    # New fields for color and size
    color = models.CharField(max_length=50, null=True)  # Optional field for color
    size = models.CharField(max_length=50, null=True)   # Optional field for size
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