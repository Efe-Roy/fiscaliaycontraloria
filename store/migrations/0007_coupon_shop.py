# Generated by Django 4.2.10 on 2024-02-29 07:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_order_shop'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='shop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='store.shop'),
        ),
    ]
