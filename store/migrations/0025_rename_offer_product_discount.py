# Generated by Django 4.0.4 on 2022-06-22 03:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0024_alter_order_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='offer',
            new_name='discount',
        ),
    ]
