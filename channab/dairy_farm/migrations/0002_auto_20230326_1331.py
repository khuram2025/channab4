# Generated by Django 3.2.16 on 2023-03-26 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dairy_farm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animal',
            name='genetics',
        ),
        migrations.AlterField(
            model_name='animal',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dairy_farm.animalcategory'),
        ),
    ]
