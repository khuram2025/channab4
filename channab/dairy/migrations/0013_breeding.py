# Generated by Django 3.2.16 on 2023-06-07 11:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0012_auto_20230605_0806'),
    ]

    operations = [
        migrations.CreateModel(
            name='Breeding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insemination_date', models.DateField()),
                ('doctor_name', models.CharField(max_length=255)),
                ('comments', models.TextField(blank=True, null=True)),
                ('test', models.CharField(choices=[('first', 'First Test'), ('second', 'Second Test'), ('third', 'Third Test')], max_length=10)),
                ('test_date', models.DateField(blank=True, null=True)),
                ('test_comments', models.TextField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('insemination_method', models.CharField(choices=[('AI', 'Artificial'), ('natural', 'Natural')], default='AI', max_length=10)),
                ('semen_info', models.TextField(blank=True, null=True)),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='breeding_records', to='dairy.animal')),
                ('bull', models.ForeignKey(blank=True, limit_choices_to={'animal_type': 'breeder', 'sex': 'male'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='natural_inseminations', to='dairy.animal')),
            ],
        ),
    ]