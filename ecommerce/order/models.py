from django.db import models
from decimal import Decimal
# Create your models here.
from django.db import models
from account.models import Account
from shop.models import ProductColor,Product


# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id
    
STATUS_CHOICES = [
        ('New', 'New'),
        ('Accepted', 'Accepted'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

class Order(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL,null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL,null=True)
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
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='New')
    ip = models.CharField(max_length=100, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.user.first_name

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Direct fields for color and size
    color = models.CharField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    
    quantity = models.IntegerField()
    product_price = models.FloatField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.title



    def subtotal(self):
        """Calculate the subtotal for this order product."""
        # Convert product_price to Decimal for accurate calculations
        product_price_decimal = Decimal(self.product_price)
        discount_amount_decimal = self.discount_amount if self.discount_amount is not None else Decimal(0)
        
        # Calculate total discount based on quantity
        total_discount = discount_amount_decimal * Decimal(self.quantity)
        
        # Calculate subtotal
        subtotal_value = (product_price_decimal * Decimal(self.quantity)) - total_discount
        
        # Ensure subtotal does not go below zero
        subtotal_value = max(subtotal_value, Decimal(0))
        
        # Debugging output
        print(f"Product: {self.product.title}, Quantity: {self.quantity}, "
              f"Unit Price: {product_price_decimal}, Discount per item: {discount_amount_decimal}, "
              f"Total Discount: {total_discount}, Subtotal: {subtotal_value}")
        
        return subtotal_value