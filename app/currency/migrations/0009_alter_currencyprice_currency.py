# Generated by Django 4.2.4 on 2023-09-06 23:41

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('currency', '0008_commondata'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currencyprice',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='currency.currency'),
        ),
    ]