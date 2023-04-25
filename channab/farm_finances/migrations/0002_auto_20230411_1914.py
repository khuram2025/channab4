# Generated by Django 3.2.16 on 2023-04-11 16:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dairy_farm', '0009_auto_20230411_1906'),
        ('farm_finances', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomeCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dairy_farm.farm')),
            ],
        ),
        migrations.CreateModel(
            name='ExpenseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dairy_farm.farm')),
            ],
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_finances.expensecategory'),
        ),
        migrations.AlterField(
            model_name='income',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='farm_finances.incomecategory'),
        ),
    ]
