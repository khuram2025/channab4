from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

class Farm(models.Model):
    name = models.CharField(max_length=100)
    admin = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='owned_farms')
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name




class CustomUserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError('The mobile number field is required')
        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(mobile, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('read_only', 'Read Only'),
    )
    mobile_validator = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Mobile number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    mobile = models.CharField(validators=[mobile_validator], max_length=17, unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    farm = models.ForeignKey(Farm, on_delete=models.SET_NULL, null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='read_only')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='accounts_custom_user_groups',
        blank=True,
        help_text=('The groups this user belongs to. A user will get all permissions '
                   'granted to each of their groups.'),
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='accounts_custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        if is_new and self.role == 'admin' and self.farm is None:
            self.create_farm_and_save()

    def create_farm_and_save(self, farm_name=None):
        if not farm_name:
            farm_name = f"{self.first_name}'s Farm"
        farm = Farm.objects.create(name=farm_name, admin=self)
        self.farm = farm
        super().save()



    def add_member(self, member):
        member.farm = self.farm
        member.save()

    def __str__(self):
        return self.mobile

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    email = models.EmailField()
    facebook = models.URLField(max_length=200, blank=True, null=True)  
    youtube = models.URLField(max_length=200, blank=True, null=True)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        self.user.first_name = self.first_name
        self.user.last_name = self.last_name
        self.user.email = self.email
        self.user.save()

    def __str__(self):
        return self.user.mobile

class SalaryComponent(models.Model):
    DURATION_CHOICES = (
        ('daily', 'Daily'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    )
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='monthly')
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='salary_components')

    def __str__(self):
        return self.name
