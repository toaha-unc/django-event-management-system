from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from events.models import UserProfile

@receiver(post_save, sender=User)
def user_post_save(sender, instance, created, **kwargs):
    """Handle user creation and profile setup"""
    if created:
        
        UserProfile.objects.get_or_create(user=instance)
        
        
        if not instance.groups.exists():
            participant_group, created = Group.objects.get_or_create(name='Participant')
            instance.groups.add(participant_group)
    
   
    if not hasattr(instance, 'profile'):
        UserProfile.objects.get_or_create(user=instance)
