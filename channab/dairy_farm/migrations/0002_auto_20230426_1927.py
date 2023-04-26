# Generated by Django 3.2.16 on 2023-04-26 16:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_rename_owner_farm_admin'),
        ('dairy_farm', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='animalcategory',
            name='category_image',
        ),
        migrations.AddField(
            model_name='animalcategory',
            name='farm',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='animal_categories', to='accounts.farm'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='animalcategory',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='animal_categories/'),
        ),
        migrations.AlterField(
            model_name='animalcategory',
            name='slug',
            field=models.SlugField(blank=True, unique=True),
        ),
        migrations.AlterField(
            model_name='animalcategory',
            name='title',
            field=models.CharField(max_length=100),
        ),
    ]
