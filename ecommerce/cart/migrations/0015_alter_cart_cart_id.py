# Generated by Django 5.1.3 on 2025-04-04 03:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0014_alter_cart_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='46769520-8553-4a8d-a361-f43edd253c63', max_length=250),
        ),
    ]
