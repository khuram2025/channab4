# Generated by Django 3.2.16 on 2023-08-23 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_salarytransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]