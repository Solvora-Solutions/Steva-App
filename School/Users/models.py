import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, first_name=None, last_name=None, role='parent', **extra_fields):
        if not email:
            raise ValueError("An email address is required.")
        if not password:
            raise ValueError("A password is required.")

        email = self.normalize_email(email)
        first_name = first_name or "First"
        last_name = last_name or "Last"
        extra_fields.setdefault('username', str(uuid.uuid4()))
        extra_fields.setdefault('is_superuser', False)

        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, first_name="Admin", last_name="User", **extra_fields):
        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, first_name, last_name, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=50,
        unique=True,
        default=uuid.uuid4,
        editable=False
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)  # ✅ added
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='parent')

    # Tracking fields
    date_joined = models.DateTimeField(default=timezone.now)  # ✅ added

    # Permissions
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"

    @property
    def is_staff(self):
        """Grant admin access for Django admin."""
        return self.role == 'admin' or self.is_superuser
