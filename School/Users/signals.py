from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User
from Parent.models import Parent


@receiver(post_save, sender=User)
def create_parent_profile(sender, instance, created, **kwargs):
    """Automatically create Parent profile for users with role='parent'."""
    if instance.role == 'parent':
        # Check if Parent profile already exists
        if not hasattr(instance, 'parent_profile'):
            # Create Parent profile if user has phone_number
            if instance.phone_number:
                Parent.objects.get_or_create(
                    user=instance,
                    defaults={
                        'phone_number': instance.phone_number,
                        'is_primary': True
                    }
                )


@receiver(post_save, sender=User)
def update_parent_profile(sender, instance, created, **kwargs):
    """Update Parent profile phone number when User phone_number changes."""
    if instance.role == 'parent' and hasattr(instance, 'parent_profile'):
        parent_profile = instance.parent_profile
        if parent_profile.phone_number != instance.phone_number and instance.phone_number:
            parent_profile.phone_number = instance.phone_number
            parent_profile.save(update_fields=['phone_number', 'updated_at'])