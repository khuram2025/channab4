# Generated by Django 3.2.16 on 2023-08-29 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0009_auto_20230829_1246'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='full_name',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='employee',
            name='role',
            field=models.CharField(default='Labour', max_length=50),
        ),
    ]
