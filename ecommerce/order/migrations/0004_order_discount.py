# Generated by Django 5.1.3 on 2025-04-12 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discount',
            field=models.FloatField(default=0.0),
        ),
    ]
