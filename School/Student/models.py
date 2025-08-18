import re
from django.db import models, transaction
from django.core.validators import MinLengthValidator, RegexValidator
from Parent.models import Parent


class StudentManager(models.Manager):
    """Custom manager for Student model with common queries."""

    def active(self):
        return self.filter(is_active=True)

    def by_class(self, class_name):
        return self.filter(current_class=class_name)

    def with_parents(self):
        return self.prefetch_related('parents')


class Student(models.Model):
    """
    Model representing a student in the academic system.
    Automatically generates unique student IDs in format SA001, SA002, etc.
    """

    student_number = models.PositiveIntegerField(
        unique=True,
        editable=False,
        null=True,
        blank=True,
        help_text="Auto-incremented numeric ID used internally for ordering."
    )

    student_id = models.CharField(
        max_length=10,
        unique=True,
        editable=False,
        null=True,
        blank=True,
        validators=[RegexValidator(
            regex=r'^SA\d{3,}$',
            message='Student ID must be in format SA001, SA002, etc.'
        )],
        help_text="Auto-generated student ID starting with SA (e.g., SA001)."
    )

    first_name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
        help_text="Student's first name."
    )

    last_name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1)],
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
        blank=True,
        help_text="Parents associated with this student."
    )

    # Audit fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the student record was created."
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the student record was last updated."
    )

    # Custom manager
    objects = StudentManager()

    def save(self, *args, **kwargs):
        """
        Override save to auto-generate student_number and student_id if not provided.
        Uses database-level locking to prevent race conditions.
        """
        if not self.student_number or not self.student_id:
            with transaction.atomic():
                last_student = (
                    Student.objects.select_for_update()
                    .exclude(student_number__isnull=True)
                    .order_by('-student_number')
                    .first()
                )

                if last_student and last_student.student_number:
                    num = last_student.student_number + 1
                else:
                    num = 1

                self.student_number = num
                self.student_id = f"SA{num:03d}"

        super().save(*args, **kwargs)

    def get_full_name(self):
        """Return the student's full name."""
        return f"{self.first_name} {self.last_name}".strip()

    def get_parent_names(self):
        """Return a comma-separated string of parent names."""
        parent_names = []
        for parent in self.parents.all():
            if hasattr(parent, 'get_full_name'):
                parent_names.append(parent.get_full_name())
            else:
                parent_names.append(str(parent))
        return ", ".join(parent_names)

    def __str__(self):
        """String representation of the student."""
        status = "Active" if self.is_active else "Inactive"
        return f"{self.student_id or 'Pending'} - {self.get_full_name()} | {self.current_class} ({status})"

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['student_number']  # ✅ safer than ordering by string ID
        indexes = [
            models.Index(fields=['student_id']),
            models.Index(fields=['student_number']),
            models.Index(fields=['is_active']),
            models.Index(fields=['current_class']),
            models.Index(fields=['-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(first_name=""),
                name="student_first_name_not_empty"
            ),
            models.CheckConstraint(
                check=~models.Q(last_name=""),
                name="student_last_name_not_empty"
            ),
            models.CheckConstraint(
                check=~models.Q(current_class=""),
                name="student_current_class_not_empty"
            ),
        ]
