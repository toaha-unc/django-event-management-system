from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator
import os

def user_profile_picture_path(instance, filename):
    """Generate upload path for user profile pictures"""
    return f'users/profile_pictures/{instance.username}/{filename}'

class CustomUser(AbstractUser):
    """Custom User model with additional fields"""
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        default='users/defaults/default_profile.svg',
        blank=True,
        null=True,
        help_text="Upload a profile picture"
    )
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        null=True,
        help_text="Phone number in international format"
    )
    
    bio = models.TextField(blank=True, null=True, max_length=500)
    address = models.TextField(blank=True, null=True)
    
    # Email verification fields
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the full name for the user."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_user_role(self):
        """Get the primary role of the user"""
        groups = self.groups.all()
        if groups.exists():
            return groups.first().name
        return "No Role"
    
    def is_admin(self):
        return self.groups.filter(name='Admin').exists()
    
    def is_organizer(self):
        return self.groups.filter(name='Organizer').exists()
    
    def is_participant(self):
        return self.groups.filter(name='Participant').exists()

# For backward compatibility, keep UserProfile model but make it a proxy
class UserProfile(models.Model):
    """Backward compatibility profile model"""
    user = models.OneToOneField('CustomUser', on_delete=models.CASCADE, related_name='legacy_profile')
    
    class Meta:
        verbose_name = 'Legacy User Profile'
        verbose_name_plural = 'Legacy User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s legacy profile"
    
    # Delegate methods to the user model
    def get_user_role(self):
        return self.user.get_user_role()
    
    def is_admin(self):
        return self.user.is_admin()
    
    def is_organizer(self):
        return self.user.is_organizer()
    
    def is_participant(self):
        return self.user.is_participant()

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a legacy profile for backward compatibility"""
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """Save the legacy profile when user is saved"""
    if hasattr(instance, 'legacy_profile'):
        instance.legacy_profile.save()
