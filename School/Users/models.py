import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)

        if 'username' not in extra_fields or not extra_fields['username']:
            extra_fields['username'] = str(uuid.uuid4())  # one-time UUID string

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('username', 'admin')
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', 'User')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=100,  # Increased size for UUID
        unique=True,
        default=uuid.uuid4,  # ✅ This is a callable, not a result
        editable=False
    )
    first_name = models.CharField(max_length=100, default='First')
    last_name = models.CharField(max_length=100, default='Last')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='parent')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"
