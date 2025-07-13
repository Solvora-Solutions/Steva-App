from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('parent', 'Parent'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='parent')
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'username'  # Change to 'email' if you want email login
    REQUIRED_FIELDS = ['email']  # This is used when creating a superuser

    def __str__(self):
        return f"{self.username} ({self.role})"
