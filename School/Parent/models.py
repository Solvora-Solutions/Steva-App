from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
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
        max_length=15,
        unique=True,
        help_text="Parent's phone number in local (024xxxxxxx) or E.164 Ghana format (+23324xxxxxxx)."
    )

    # Status fields
    verified = models.BooleanField(default=False, help_text="Phone verification status.")
    is_primary = models.BooleanField(default=True, help_text="Is this the primary contact?")

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True, help_text="Profile creation timestamp.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp.")

    def clean(self):
        """Custom validation."""
        super().clean()

        # Ensure linked user has parent role
        if self.user_id and self.user.role != 'parent':
            raise ValidationError({'user': 'Linked user must have role "parent".'})

        if self.phone_number:
            phone = self._format_phone_number(self.phone_number)

            # Validate Ghana mobile prefixes
            valid_prefixes = getattr(
                settings,
                "GHANA_MOBILE_PREFIXES",
                ['024', '054', '055', '059', '020', '050', '026', '056', '027', '057', '028', '058']
            )
            local_prefix = "0" + phone[4:6]  # e.g. +23324xxxxxxx → 024
            if local_prefix not in valid_prefixes:
                raise ValidationError({
                    'phone_number': 'Phone number must start with a valid Ghana mobile prefix.'
                })

    def save(self, *args, **kwargs):
        """Normalize before saving."""
        if self.phone_number:
            self.phone_number = self._format_phone_number(self.phone_number)

        # Validate
        self.full_clean()
        super().save(*args, **kwargs)

    def _format_phone_number(self, phone):
        """Convert phone number to E.164 (+233xxxxxxxxx)."""
        if not phone:
            return phone

        phone = ''.join(filter(str.isdigit, phone))

        # Local format: 0xxxxxxxxx → +233xxxxxxxxx
        if phone.startswith('0') and len(phone) == 10:
            return f"+233{phone[1:]}"

        # Ghana format without plus: 233xxxxxxxxx → +233xxxxxxxxx
        if phone.startswith('233') and len(phone) == 12:
            return f"+{phone}"

        # Already correct E.164 format
        if phone.startswith('233') and len(phone) == 12:
            return f"+{phone}"

        if phone.startswith('+233') and len(phone) == 13:
            return phone

        raise ValidationError({'phone_number': 'Invalid Ghana phone number format.'})

    @property
    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}".strip()

    @property
    def display_phone(self):
        """Return local style (0xxxxxxxxx)."""
        if not self.phone_number:
            return ""
        return f"0{self.phone_number[4:]}"  # Convert +233xxxxxxx → 0xxxxxxxxx

    @property
    def total_children(self):
        return self.students.filter(is_active=True).count()

    @property
    def active_children(self):
        return self.students.filter(is_active=True)

    def get_payment_history(self):
        return []

    def get_outstanding_fees(self):
        return 0

    def verify_phone(self):
        self.verified = True
        self.save(update_fields=['verified', 'updated_at'])

    def unverify_phone(self):
        self.verified = False
        self.save(update_fields=['verified', 'updated_at'])

    def __str__(self):
        return f"{self.full_name} - {self.user.email}"

    class Meta:
        verbose_name = "Parent"
        verbose_name_plural = "Parents"
        ordering = ['user__first_name', 'user__last_name']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['verified']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(phone_number=''),
                name='parent_phone_not_empty'
            ),
        ]
