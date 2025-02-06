from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import Account

# Create your models here.

class Promotion(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.code
class AppliedPromotion(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    promo_code = models.CharField(max_length=50)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.promo_code} applied by {self.user.username}"
    



class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # Discount in percentage
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code