# Generated by Django 5.1.3 on 2025-04-02 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0012_alter_cart_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='bbacf71c-1da2-4159-a2fe-05fa713e505f', max_length=250),
        ),
    ]
