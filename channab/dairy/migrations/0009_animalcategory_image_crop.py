# Generated by Django 3.2.16 on 2023-05-27 08:03

from django.db import migrations
import image_cropping.fields


class Migration(migrations.Migration):

    dependencies = [
        ('dairy', '0008_delete_family'),
    ]

    operations = [
        migrations.AddField(
            model_name='animalcategory',
            name='image_crop',
            field=image_cropping.fields.ImageRatioField('image', '500x500', adapt_rotation=False, allow_fullsize=False, free_crop=False, help_text=None, hide_image_field=False, size_warning=False, verbose_name='image crop'),
        ),
    ]
