# Generated by Django 4.0.4 on 2022-06-23 04:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0027_cartitem_disc_pice'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='disc_pice',
        ),
    ]
