from django.db import models
from django.core.validators import MinLengthValidator
from Parent.models import Parent

class Student(models.Model):
    student_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        null=True, blank=True,  # ✅ Allow null temporarily for existing rows
        help_text="Custom student ID starting with SA."
    )
    first_name = models.CharField(
        default="Unknown",
        max_length=100,
        help_text="Student's first name."
    )
    last_name = models.CharField(
        default="Unknown",
        max_length=100,
        help_text="Student's last name."
    )
    current_class = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
        help_text="Current academic class or grade level."
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Indicates if the student is currently enrolled."
    )
    parents = models.ManyToManyField(
        Parent,
        related_name='students',
        help_text="Parents associated with this student."
    )

    def save(self, *args, **kwargs):
        if not self.student_id:  # Auto-generate only when blank
            last_student = Student.objects.exclude(student_id__isnull=True).order_by('-id').first()
            if last_student and last_student.student_id:
                try:
                    num = int(last_student.student_id.replace("SA", "")) + 1
                except ValueError:
                    num = 1
            else:
                num = 1
            self.student_id = f"SA{num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_id or 'N/A'} - {self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['student_id']
