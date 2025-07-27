from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from Users.models import User

class Parent(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='parent_profile',
        limit_choices_to={'role': 'parent'},
        help_text="Linked user account (must have role='parent')."
    )

    phone_number = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{9,15}$',
                message="Phone number must be in the format: '+233123456789'. Up to 15 digits allowed."
            )
        ],
        help_text="Parent's phone number (international format)."
    )

    admission_date = models.DateField(
        default=timezone.now,
        help_text="Date the parent was registered in the system."
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Profile creation timestamp."
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.user.email}"

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        ordering = ['user__email']
