# Generated by Django 5.1.3 on 2025-04-10 04:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0002_alter_order_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20),
        ),
    ]
