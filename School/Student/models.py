from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator
from Users.models import User
from Parent.models import Parent


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        help_text="Linked user account for the student."
    )
    parent = models.ForeignKey(
        Parent,
        on_delete=models.CASCADE,
        related_name='children',
        help_text="The parent responsible for this student."
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
        name = self.user.get_full_name() if self.user else "Unnamed Student"
        return f"{name} - {self.current_class}"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['user__last_name', 'user__first_name']
