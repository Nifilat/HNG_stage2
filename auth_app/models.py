from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, firstName, lastName, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, userId=uuid.uuid4(), firstName=firstName, lastName=lastName, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    userId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    firstName = models.CharField(max_length=30, null=False)
    lastName = models.CharField(max_length=30, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=128, null=False)
    phone = models.CharField(max_length=15, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    def __str__(self):
        return self.email
    

class Organisation(models.Model):
    orgId = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, related_name='organisations')
