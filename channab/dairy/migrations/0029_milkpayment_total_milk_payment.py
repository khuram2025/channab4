# Generated by Django 3.2.16 on 2023-09-13 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0028_auto_20230913_1142'),
    ]

    operations = [
        migrations.AddField(
            model_name='milkpayment',
            name='total_milk_payment',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7),
        ),
    ]
