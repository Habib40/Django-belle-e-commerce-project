# Generated by Django 5.1.3 on 2024-12-20 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0010_alter_cart_cart_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='9c669a6b-4fd9-41d1-8284-0d1e2ce8fc61', max_length=250),
        ),
    ]
