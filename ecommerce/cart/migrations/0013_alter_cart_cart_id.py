# Generated by Django 5.1.3 on 2024-12-29 06:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0012_alter_cart_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='766b6602-5bb3-4e3c-ad39-6d3ff1b5d30a', max_length=250),
        ),
    ]
