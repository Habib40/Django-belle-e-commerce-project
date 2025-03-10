# shop/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderProduct

@receiver(post_save, sender=Order)
def update_product_stock_on_order_accept(sender, instance, created, **kwargs):
    if created:
        return  # Only react to updates, not creations

    if instance.status == 'Accepted':
        order_products = OrderProduct.objects.filter(order=instance)
        for order_product in order_products:
            product = order_product.product
            if product.quantity_left >= order_product.quantity:
                product.items_sold += order_product.quantity  # Increase sold items
                product.quantity_sold += order_product.quantity  # Increase sold items
                product.quantity_left -= order_product.quantity #Decrease available quantity
                product.stock -= order_product.quantity
                product.save()
            else:
                # Handle insufficient stock
                print(f"Not enough stock for {product.title}. Available: {product.quantity_left}, Requested: {order_product.quantity}")