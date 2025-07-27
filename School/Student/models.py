from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from Users.models import User

class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="Linked user account for the student."
    )

    parents = models.ManyToManyField(
        User,
        related_name='linked_students',
        limit_choices_to={'role': 'parent'},
        help_text="Parent users associated with this student."
    )

    current_class = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
        help_text="Current academic class or grade level."
    )

    admission_date = models.DateField(
        default=timezone.now,
        help_text="Date the student was admitted."
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the student is currently enrolled."
    )

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} - {self.current_class}"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['user__email']
