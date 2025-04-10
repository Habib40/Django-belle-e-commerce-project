from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from account.models import Account
from django.utils import timezone

# Create your models here.

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
    discount = models.DecimalField(max_digits=5, decimal_places=2,
                                   validators=[MinValueValidator(0), MaxValueValidator(100)])  # Allow decimal percentages
    active = models.BooleanField(default=True)
    usage_limit = models.PositiveIntegerField(default=1, help_text="Limit of how many times this coupon can be used")
    used_count = models.PositiveIntegerField(default=0)  # Current usage count

    def __str__(self):
        return self.code

    def is_valid(self):
        
        return self.active and self.valid_from <= timezone.now() <= self.valid_to and (self.used_count < self.usage_limit)