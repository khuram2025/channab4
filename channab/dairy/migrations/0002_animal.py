# Generated by Django 3.2.16 on 2023-04-28 05:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('dairy', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='animals/')),
                ('dob', models.DateField(verbose_name='Date of Birth')),
                ('purchase_cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('sold', 'Sold')], default='active', max_length=10)),
                ('sex', models.CharField(choices=[('male', 'Male'), ('female', 'Female')], max_length=6)),
                ('animal_type', models.CharField(choices=[('breeder', 'Breeder'), ('pregnant', 'Pregnant'), ('dry', 'Dry'), ('milking', 'Milking'), ('preg_milking', 'Pregnant Milking'), ('calf', 'Calf'), ('other', 'Other')], default='other', max_length=20)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animals', to='dairy.animalcategory')),
                ('farm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animals', to='accounts.farm')),
            ],
        ),
    ]