from django.db import models

from django.utils.text import slugify
from django.utils import timezone
from accounts.models import Farm

class AnimalCategory(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to='animal_categories/', blank=True, null=True)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animal_categories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Animal(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animals')
    tag = models.CharField(max_length=100, unique=True)
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
        ('preg_milking', 'Pregnant Milking'),
        ('calf', 'Calf'),
        ('other', 'Other'),
    ]
    animal_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')

    def __str__(self):
        return f'{self.tag} ({self.category.title})'
    

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