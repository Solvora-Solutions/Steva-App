from django.db import models
from django.core.validators import RegexValidator
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
        max_length=15,  # E.164 format max length
        unique=True,  # Prevent duplicate phone numbers
        validators=[
            RegexValidator(
                regex=r'^\+233[2-9][0-9]{8}$',
                message="Enter a valid phone number in E.164 Ghana format (e.g., +233241234567).",
            )
        ],
        help_text="Parent's phone number stored in E.164 Ghana format (e.g., +233241234567)."
    )

    # Status fields
    verified = models.BooleanField(
        default=False,
        help_text="Indicates if the parent has completed phone verification."
    )
    
    is_primary = models.BooleanField(
        default=True,
        help_text="Indicates if this is the primary contact for students."
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True, help_text="Profile creation timestamp.")
    updated_at = models.DateTimeField(auto_now=True, help_text="Last update timestamp.")

    def clean(self):
        """Custom validation."""
        super().clean()

        # Ensure linked user has parent role
        if self.user_id and self.user.role != 'parent':
            raise ValidationError({'user': 'Linked user must have role "parent".'})

        # Validate Ghana mobile prefixes
        if self.phone_number:
            phone = self.phone_number.strip()
            valid_prefixes = getattr(
                settings,
                "GHANA_MOBILE_PREFIXES",
                ['024', '054', '055', '059', '020', '050', '026', '056', '027', '057', '028', '058']
            )
            # Example: +23324xxxxxxx → prefix = 024
            if phone.startswith('+233'):
                local_prefix = '0' + phone[4:6] + phone[6:7]
                if local_prefix not in valid_prefixes:
                    raise ValidationError({
                        'phone_number': 'Phone number must start with a valid Ghana mobile prefix.'
                    })

    def save(self, *args, **kwargs):
        """Override save to format phone number and validate."""
        if self.phone_number:
            self.phone_number = self._format_phone_number(self.phone_number)

        # Run validation
        self.full_clean()
        super().save(*args, **kwargs)

    def _format_phone_number(self, phone):
        """Convert phone number to E.164 (+233xxxxxxxxx)."""
        if not phone:
            return phone

        # Remove spaces, hyphens, brackets
        phone = ''.join(filter(str.isdigit, phone.replace('+', '')))
        
        # Handle local format 0xxxxxxxxx
        if phone.startswith('0') and len(phone) == 10:
            return f"+233{phone[1:]}"
        
        # Handle already E.164 (+233xxxxxxxxx)
        if phone.startswith('233') and len(phone) == 12:
            return f"+{phone}"
        
        return phone  # fallback

    @property
    def full_name(self):
        """Return parent's full name."""
        return f"{self.user.first_name} {self.user.last_name}".strip()

    @property
    def display_phone(self):
        """Return formatted phone number for display (local style)."""
        if not self.phone_number:
            return ""
        return f"0{self.phone_number[4:]}"  # Convert +233xxxxxxx → 0xxxxxxxxx

    @property
    def total_children(self):
        """Get count of children for this parent."""
        return self.students.filter(is_active=True).count()

    @property
    def active_children(self):
        """Get queryset of active children."""
        return self.students.filter(is_active=True)

    def get_payment_history(self):
        """Get payment history for all children (placeholder)."""
        return []

    def get_outstanding_fees(self):
        """Get total outstanding fees for all children (placeholder)."""
        return 0

    def verify_phone(self):
        """Mark parent's phone as verified."""
        self.verified = True
        self.save(update_fields=['verified', 'updated_at'])

    def unverify_phone(self):
        """Mark parent's phone as unverified."""
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
            models.Index(fields=['user']),  # added for performance
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(phone_number=''),
                name='parent_phone_not_empty'
            ),
        ]
