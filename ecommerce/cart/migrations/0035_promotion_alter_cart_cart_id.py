# Generated by Django 5.1.3 on 2025-01-21 13:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0034_alter_cart_cart_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('discount_percentage', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.AlterField(
            model_name='cart',
            name='cart_id',
            field=models.CharField(blank=True, default='bc59e7bf-22a7-46a2-b726-35de1dff6476', max_length=250),
        ),
    ]
