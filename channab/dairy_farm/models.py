from django.db import models
from django.contrib.auth import get_user_model
import datetime
from taggit.managers import TaggableManager
from django.db import models
from django.utils.text import slugify
from datetime import date
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from accounts.models import Farm


class AnimalCategory(models.Model):
    title = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, editable=False, default='')
    category_image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(AnimalCategory, self).save(*args, **kwargs)



User = get_user_model()



class Genetics(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class FemaleAnimalManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(sex='Female')
    
class Animal(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='animals')
    tag = models.CharField(max_length=100)
    image = models.ImageField(upload_to='animals/', blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    mother = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children_mother", limit_choices_to={'sex': 'Female'})
    father = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children_father", limit_choices_to={'sex': 'Male'})
    purchase_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('sold', 'Sold'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', blank=True, null=True)
    SEX_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    sex = models.CharField(max_length=6, choices=SEX_CHOICES)
    
  
    category = models.ForeignKey(AnimalCategory, on_delete=models.CASCADE)
    objects = models.Manager()  # Default manager
    females = FemaleAnimalManager()  # Custom manager for female animals

    @property
    def children(self):
        return self.children_mother.all() | self.children_father.all()

    @property
    def number_of_children(self):
        male_children = self.children_mother.filter(sex="Male").count() + self.children_father.filter(sex="Male").count()
        female_children = self.children_mother.filter(sex="Female").count() + self.children_father.filter(sex="Female").count()
        return {
            "male": male_children,
            "female": female_children,
            "total": male_children + female_children
        }

    def __str__(self):
        return f"{self.tag} ({self.category})"
    
    
    
    @property
    def age(self):
        if self.dob:
            today = date.today()
            age = today.year - self.dob.year - ((today.month, today.day) < (self.dob.month, self.dob.day))
            return age
        return None


class MilkRecord(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, limit_choices_to={'sex': 'Female'})
    date = models.DateField(default=timezone.now)
    first_time = models.DecimalField(max_digits=5, decimal_places=2)
    second_time = models.DecimalField(max_digits=5, decimal_places=2)
    third_time = models.DecimalField(max_digits=5, decimal_places=2)

    @property
    def total_milk(self):
        return self.first_time + self.second_time + self.third_time




class Member(AbstractUser):
    image = models.ImageField(upload_to='members/', blank=True, null=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    job_title = models.CharField(max_length=100)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='dairy_farm_member_groups',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='dairy_farm_member_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'mobile_number'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'email']

    def __str__(self):
        return self.username
class Farm(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    members = models.ManyToManyField(Member, through='FarmMember')

    def __str__(self):
        return self.name

class FarmMember(models.Model):
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        unique_together = ('user', 'farm')

    def __str__(self):
        return f"{self.user.username} - {self.farm.name} - {self.role}"
    

class AnimalRelation(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='relations')
    related_animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='related_animals')
    relation_type = models.CharField(max_length=50, choices=(('mother', 'Mother'), ('father', 'Father'), ('child', 'Child')))

    def __str__(self):
        return f"{self.animal.tag} - {self.relation_type} - {self.related_animal.tag}"

class AnimalWeight(models.Model):
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE)
    date = models.DateField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.animal.tag} - {self.date} - {self.weight} KGs"
