from django.contrib.auth.models import AbstractUser
from django.db import models
from Users import models as Users


class Student(models.Model):
    user = models.OneToOneField(
        Users.User,
        on_delete=models.CASCADE,)
    current_class = models.CharField(max_length=100)

    
   

   