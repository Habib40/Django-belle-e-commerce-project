# Generated by Django 5.1.3 on 2024-12-04 03:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_delete_color'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcolor',
            name='size',
            field=models.CharField(choices=[('xs', 'Extra Small'), ('s', 'Small'), ('m', 'Medium'), ('l', 'Large'), ('xl', 'Extra Large'), ('xxl', 'Double Extra Large'), ('3xl', 'Triple Extra Large'), ('4xl', 'Quadruple Extra Large')], default='m', max_length=50),
        ),
    ]
