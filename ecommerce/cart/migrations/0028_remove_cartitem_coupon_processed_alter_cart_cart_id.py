# Generated by Django 5.1.3 on 2025-04-13 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0027_alter_cart_cart_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='coupon_processed',
        ),
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='52c19409-87be-48c8-9ebe-0a50a2e32940', max_length=250),
        ),
    ]
