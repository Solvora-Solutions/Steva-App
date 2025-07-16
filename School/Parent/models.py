from django.contrib.auth.models import AbstractUser
from django.db import models
from Users.models import User
from Student.models import Student



class Parent(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    children = models.ManyToManyField(Student, related_name='parents')

    def __str__(self):
        return self.user.username
