from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.urls import reverse
# Create your models here.


class MyAccountManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, email, password=None):
        if not email:
            raise ValueError('User must have an email address')
        if not username:
            raise ValueError('User must have a username')
        
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name
        )
        
        user.set_password(password)  # Set the password
        user.is_active = True  # Set user to active upon creation
       
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, email, password):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.is_superuser = True  # Set superuser flag
        user.save(using=self._db)
        return user
        
class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)  # Change to EmailField
    phone_number = models.CharField(max_length=11, blank=True)  # Optional field
    
    join_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)  # Updated to now on user login

    is_admin = models.BooleanField(default=False) 
    is_staff = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)  # Default to active
    is_superuser = models.BooleanField(default=False)  # Use is_superuser field

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    objects = MyAccountManager()

    def has_perm(self, perm, obj=None):
        return self.is_admin or self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_admin or self.is_superuser

    def __str__(self):
        return self.email  # Return email as string representation
    