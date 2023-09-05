from datetime import date, timedelta
from django.db import models
from datetime import datetime

from django.utils.text import slugify
from django.utils import timezone
from accounts.models import Farm
from PIL import Image, ExifTags
from io import BytesIO
from django.core.files import File
from image_cropping import ImageRatioField
from django.core.files.uploadedfile import SimpleUploadedFile
import io 

class AnimalCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='animal_categories/', blank=True, null=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animal_categories', blank=True, null=True)
    is_site_level = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.is_site_level:
            self.farm = None
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Animal(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animals')
    tag = models.CharField(max_length=100)
    
    image = models.ImageField(upload_to='animals/', blank=True, null=True)
    dob = models.DateField(verbose_name='Date of Birth')
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('sold', 'Sold'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)
    category = models.ForeignKey(AnimalCategory, on_delete=models.CASCADE, related_name='animals')
    TYPE_CHOICES = [
        ('breeder', 'Breeder'),
        ('pregnant', 'Pregnant'),
        ('dry', 'Dry'),
        ('milking', 'Milking'),
        ('preg_milking', 'Pre-Milk'),
        ('calf', 'Calf'),
        ('other', 'Other'),
    ]
    animal_type = models.CharField(max_length=200, choices=TYPE_CHOICES, default='other')
    ANIMAL_TYPE_CHOICES_DICT = dict(TYPE_CHOICES)

    mother = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children_mother')
    father = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children_father')
    
    def _rotate_image(self, image):
        if hasattr(image, '_getexif'):
            exif_data = image._getexif()
            if exif_data is not None:
                for tag, value in list(exif_data.items()):
                    if tag in ExifTags.TAGS:
                        if ExifTags.TAGS[tag] == 'Orientation':
                            if value == 3:
                                image = image.rotate(180, expand=True)
                            elif value == 6:
                                image = image.rotate(-90, expand=True)
                            elif value == 8:
                                image = image.rotate(90, expand=True)
                            break
        return image
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['farm', 'tag'], name='unique_farm_tag')
        ]

    def save(self, *args, **kwargs):
        if self.mother == self or self.father == self:
            raise ValidationError('An animal cannot be its own parent.')
        if self.mother and self.mother.sex != 'female':
            raise ValidationError('Mother must be a female animal.')
        if self.father and self.father.sex != 'male':
            raise ValidationError('Father must be a male animal.')
        if self.mother and self in self.mother.get_descendants(include_children=False):
            raise ValidationError('Invalid parent-child relationship.')
        if self.father and self in self.father.get_descendants(include_children=False):
            raise ValidationError('Invalid parent-child relationship.')

        if self.image:
            # Open the original image
            image = Image.open(self.image)

            # Rotate the image if necessary based on the EXIF orientation
            image = self._rotate_image(image)

            # Resize the image while maintaining the aspect ratio
            max_size = (800, 800)
            image.thumbnail(max_size)

            # If the image has transparency (an alpha channel), convert it to RGB
            if image.mode in ('RGBA', 'LA'):
                background = Image.new(image.mode[:-1], image.size, '#FFFFFF')
                background.paste(image, image.split()[-1]) # alpha channel is used as mask
                image = background

            # Create a BytesIO object to hold the compressed image data
            image_io = io.BytesIO()

            # Save the image to the BytesIO object with JPEG format and quality of 70
            image.save(image_io, format='JPEG', quality=70)

            # Calculate the size of the compressed image
            image_size = image_io.tell()

            # If the image size is larger than 50 KB, further compress it
            if image_size > 50000:
                # Calculate the desired compression ratio
                compression_ratio = 50000 / image_size

                # Create a new BytesIO object to hold the further compressed image data
                compressed_image_io = io.BytesIO()

                # Adjust the quality based on the compression ratio and save the image
                image.save(compressed_image_io, format='JPEG', quality=int(compression_ratio * 70))

                # Set the content of the image field to the further compressed image
                self.image = SimpleUploadedFile(self.image.name, compressed_image_io.getvalue())

        super().save(*args, **kwargs)


    def get_descendants(self, include_children=True):
        descendants = set()
        if include_children:
            for child in self.children_mother.all():
                descendants.add(child)
                descendants.update(child.get_descendants())
            for child in self.children_father.all():
                descendants.add(child)
                descendants.update(child.get_descendants())
        return descendants
    @property
    def all_children(self):
        return self.children_mother.all() | self.children_father.all()
    
    @property
    def siblings(self):
        mother_children = self.mother.children_mother.all() if self.mother else Animal.objects.none()
        father_children = self.father.children_father.all() if self.father else Animal.objects.none()
        return (mother_children | father_children).exclude(id=self.id)
    
    def __str__(self):
        return f'{self.tag} ({self.category.title})'



from django.db.models import Q

from django.core.exceptions import ValidationError



class MilkRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, limit_choices_to={'sex': 'female'})
    date = models.DateField(default=timezone.now)
    first_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    second_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    third_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    
    @property
    def total_milk(self):
        first_time = self.first_time or 0
        second_time = self.second_time or 0
        third_time = self.third_time or 0
        return first_time + second_time + third_time

    
class AnimalWeight(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='weights')
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.animal.tag} - {self.weight_kg} kg on {self.date}'




class Breeding(models.Model):
    female_animal = models.ForeignKey(
        Animal,
        on_delete=models.CASCADE,
        related_name='breeding_events',
        limit_choices_to={'sex': 'female'},
        null=True
    )
    
    date_of_insemination = models.DateField(default=datetime.today)
    
    BREEDING_METHOD_CHOICES = [
        ('natural', 'Natural'),
        ('artificial', 'Artificial')
    ]
    breeding_method = models.CharField(max_length=10, choices=BREEDING_METHOD_CHOICES)
    
    bull = models.ForeignKey(
        Animal,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='natural_breeding_events',
        limit_choices_to={'sex': 'male', 'animal_type': 'breeder'}
    )
    
    semen_tag = models.CharField(max_length=100, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    
    lactation_number = models.PositiveIntegerField(blank=True, null=True)
    
    attempt = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        # If this is not a new object
        if self.pk:
            prev_breeding = Breeding.objects.filter(female_animal=self.female_animal).order_by('-date_of_insemination').first()
            
            if prev_breeding:
                if prev_breeding.lactation_number:
                    self.lactation_number = prev_breeding.lactation_number + 1
                if prev_breeding.attempt:
                    self.attempt = prev_breeding.attempt + 1
        
        super(Breeding, self).save(*args, **kwargs)
    
    def clean(self):
        # Check if the correct method-related field is filled
        if self.breeding_method == 'natural' and not self.bull:
            raise ValidationError('A bull must be selected for natural breeding.')
        if self.breeding_method == 'artificial' and not self.semen_tag:
            raise ValidationError('A semen tag number must be provided for artificial breeding.')

        # Ensure that non-related fields are empty
        if self.breeding_method == 'natural' and self.semen_tag:
            raise ValidationError('Semen tag number must be empty for natural breeding.')
        if self.breeding_method == 'artificial' and self.bull:
            raise ValidationError('Bull must not be selected for artificial breeding.')

    class Meta:
        # Ensure that one animal doesn't have multiple breeding records on the same day
        constraints = [
            models.UniqueConstraint(fields=['female_animal', 'date_of_insemination'], name='unique_animal_insemination_date')
        ]

class Customer(models.Model):
    name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)  # Making it optional
    created_date = models.DateField(default=date.today, editable=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, blank=True, null=True)
    # Any other relevant details about the customer

    def __str__(self):
        return self.name


class MilkSale(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    first_sale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    second_sale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    third_sale = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    price_per_liter = models.DecimalField(max_digits=5, decimal_places=2)
    total_price = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, blank=True, null=True)
   
    def save(self, *args, **kwargs):
        total_liters = (self.first_sale or 0) + (self.second_sale or 0) + (self.third_sale or 0)
        # Only update total_price if it's not provided
        if self.total_price is None:
            self.total_price = total_liters * self.price_per_liter
        super().save(*args, **kwargs)


    @property
    def total_liters_sold(self):
        return (self.first_sale or 0) + (self.second_sale or 0) + (self.third_sale or 0)

    @property
    def is_valid_sale(self):
        return self.total_liters_sold <= self.milk_record.total_milk

    def __str__(self):
        return f"{self.total_liters_sold} liters to {self.customer.name} on {self.date}"
