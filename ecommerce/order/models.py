from django.db import models
from decimal import Decimal
# Create your models here.
from django.db import models
from account.models import Account
#from shop.models import Product


class Payment(models.Model):
    user = models.ForeignKey(Account , on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255)
    payment_method = models.CharField(max_length=50)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.payment_id} - {self.payment_method}"
    
    
STATUS_CHOICES = [
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]



class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=30)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=11)
    email = models.CharField(max_length=50)
    address_line_1 = models.CharField(max_length=100)
    address_line_2 = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    order_note = models.CharField(max_length=150, blank=True)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    ip = models.CharField(max_length=100, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # New field for payment method
    payment_method = models.CharField(max_length=50, default='credit_card',null=True)  # Add this line
    cash_on_delivery = models.BooleanField(default=False)  # Add this line
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey('shop.Product', on_delete=models.CASCADE)
    
    # Direct fields for color and size
    color = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    discount = models.FloatField(default=0)  # Add discount field
    quantity =models.IntegerField()
    product_price = models.FloatField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title



    