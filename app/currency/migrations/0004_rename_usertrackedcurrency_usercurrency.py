# Generated by Django 4.2.4 on 2023-09-06 05:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('currency', '0003_usertrackedcurrency'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserTrackedCurrency',
            new_name='UserCurrency',
        ),
    ]
