# Generated by Django 5.1.3 on 2024-12-15 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_remove_cartitem_last_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='color',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
