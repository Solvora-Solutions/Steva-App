from django.db import models
from Users.models import User

class Staff(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

# Create your models here.
