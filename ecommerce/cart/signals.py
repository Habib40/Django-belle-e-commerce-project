from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from .models import Cart, CartItem

@receiver(post_save, sender=CartItem)
def reduce_discount_after_coupon(sender, instance, **kwargs):
    """
    Triggered after coupon is applied to cart.
    Reduces product discount_amounts ONCE.
    """
    if instance.coupon_applied and instance.coupon and not instance.coupon_processed:
        cart_items = CartItem.objects.filter(cart=instance, is_active=True)

        for item in cart_items:
            product = item.product
            if product.discount_amount:
                # Example: reduce discount by 10%
                product.discount_amount - instance.apply_coupon()  # or subtract a flat value
                product.save()

        # Prevent reprocessing
        instance.coupon_processed = True
        instance.save(update_fields=['coupon_processed'])
