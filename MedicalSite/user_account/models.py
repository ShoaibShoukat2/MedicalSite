from django.db import models
from django.contrib.auth.models import BaseUserManager,AbstractBaseUser,PermissionsMixin
from django.db.models import Q
from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password

'''Custom User Manager'''
class UserManager(BaseUserManager):
    def create_user(self, email,  name=None, phone_no=None, password=None, password2=None,**extra_fields):
        
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            name=name,
            phone_no= phone_no
        )

        user.set_password(password)

        user.is_user = True
        user.save(using=self._db)
        # view_product_permission = Permission.objects.get(codename='view_product')
        # user.user_permissions.add(view_product_permission)

        return user
    

    def create_superuser(self, email,name=None, phone_no=None, password=None,**extra_fields):
        user = self.create_user(
            email,
            password=password,
            name=name,
            phone_no= phone_no
        )
        user.is_admin = True
        user.is_superuser =True
        user.save(using=self._db)
        return user





'''Custom User Model'''
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        verbose_name='Email',
        max_length=255,
        unique=True,
    )
    name = models.CharField(max_length=200, null=True, blank=True)
    is_user = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    phone_no = models.CharField(max_length=150, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)  # Add address field
    avatar = models.ImageField(upload_to="avatarimage/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.name if self.name else self.email}"

    @property
    def is_staff(self):
        return self.is_admin or self.is_user
    
    
    
from django.db import models

class Patient(models.Model):
    GREETING_CHOICES = [
        ('Mr.', 'Mr.'),
        ('Other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('Men', 'Men'),
        ('Women', 'Women'),
    ]

    greeting = models.CharField(max_length=5, choices=GREETING_CHOICES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    mobile_phone = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Use Django's built-in password hashing later
    profile_photo = models.ImageField(upload_to='patient_photos/', null=True, blank=True)  # Profile photo field

    def __str__(self):
        return f"{self.greeting} {self.first_name} {self.last_name}"

    
class Practitioner(models.Model):
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    DOCTOR_TYPE_CHOICES = [
        ('health_professional', 'A health professional'),
        ('other', 'Other'),
    ]

    SPECIALTY_CHOICES = [
        ('occupational_therapist', 'Occupational Therapist'),
        ('physiotherapist', 'Physiotherapist'),
        ('neuropsychologist', 'Neuropsychologist'),
        ('speech_therapist', 'Speech Therapist'),
        ('psychologist', 'Psychologist'),
        ('chiropractor', 'Chiropractor'),
        ('nutritionist', 'Nutritionist'),
        ('general_practitioner', 'General Practitioner'),
    ]

    CIVILITY_CHOICES = [
        ('m', 'M.'),
        ('mme', 'Mme'),
        ('mlle', 'Mlle'),
    ]

    doctor_type = models.CharField(max_length=20, choices=DOCTOR_TYPE_CHOICES)
    specialty = models.CharField(max_length=30, choices=SPECIALTY_CHOICES)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    civility = models.CharField(max_length=5, choices=CIVILITY_CHOICES)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    terms_accepted = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='practitioner_photos/', null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    # New fields for gender and location
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"{self.get_civility_display()} {self.first_name} {self.last_name} ({self.get_specialty_display()})"
