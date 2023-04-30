# Generated by Django 3.2.16 on 2023-04-29 07:41

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0002_animal'),
    ]

    operations = [
        migrations.CreateModel(
            name='MilkRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('first_time', models.DecimalField(decimal_places=2, max_digits=5)),
                ('second_time', models.DecimalField(decimal_places=2, max_digits=5)),
                ('third_time', models.DecimalField(decimal_places=2, max_digits=5)),
                ('animal', models.ForeignKey(limit_choices_to={'sex': 'Female'}, on_delete=django.db.models.deletion.CASCADE, to='dairy.animal')),
            ],
        ),
    ]