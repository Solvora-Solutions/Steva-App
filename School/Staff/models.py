from django.db import models
from Users.models import User

class Staff(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='staff_profile',
        help_text="Linked user account for the staff."
    )
    position = models.CharField(
        max_length=100,
        help_text="Job title or role of the staff member."
    )

    def __str__(self):
        return f"{self.user.email} - {self.position}"

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff"
        ordering = ['user__email']
