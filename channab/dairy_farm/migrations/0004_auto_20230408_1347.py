# Generated by Django 3.2.16 on 2023-04-08 10:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dairy_farm', '0003_rename_name_animalcategory_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalcategory',
            name='category_icon',
            field=models.ImageField(blank=True, null=True, upload_to='category_icons/'),
        ),
        migrations.AddField(
            model_name='animalcategory',
            name='category_image',
            field=models.ImageField(blank=True, null=True, upload_to='category_images/'),
        ),
        migrations.AddField(
            model_name='animalcategory',
            name='slug',
            field=models.SlugField(default='', editable=False, unique=True),
        ),
    ]
