# Generated by Django 4.2.4 on 2023-09-06 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0004_rename_usertrackedcurrency_usercurrency'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usercurrency',
            old_name='threshold_price',
            new_name='threshold',
        ),
    ]
