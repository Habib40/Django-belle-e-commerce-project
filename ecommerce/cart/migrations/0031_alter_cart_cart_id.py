# Generated by Django 5.1.3 on 2025-01-19 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0030_alter_cart_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='42ddc39e-8624-499d-8916-003cd193283e', max_length=250),
        ),
    ]
