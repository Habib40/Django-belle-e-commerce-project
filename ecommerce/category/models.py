from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User  # If you are using Django's built-in User model

# class Cart(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)  # Assuming each user has one cart
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Cart of {self.user.username}"

# class CartItem(models.Model):
#     user = models.ForeignKey(Account,on_delete=models.CASCADE,null=True)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE,null=True)
#     variations = models.ManyToManyField(Variation,blank=True)
#     cart = models.ForeignKey(Cart,on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     is_active = models.BooleanField(default=True)
    
#     def sub_total(self):
#         return self.product.price * self.quantity
    
#     def __str__(self):
#         return f"Cart item for {self.product.name}"
