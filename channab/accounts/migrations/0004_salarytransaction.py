# Generated by Django 3.2.16 on 2023-05-07 13:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_profile_joining_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalaryTransaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount_paid', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.salarycomponent')),
                ('farm_member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_transactions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
