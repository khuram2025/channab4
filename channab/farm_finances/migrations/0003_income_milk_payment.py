# Generated by Django 3.2.16 on 2023-09-13 11:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0030_auto_20230913_1148'),
        ('farm_finances', '0002_expense_salary_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='income',
            name='milk_payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='dairy.milkpayment'),
        ),
    ]
