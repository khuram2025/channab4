# Generated by Django 3.2.16 on 2023-09-04 16:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0022_auto_20230904_1858'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='created_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]