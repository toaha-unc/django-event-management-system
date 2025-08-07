from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Event(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='events')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    # RSVP participants
    rsvp_participants = models.ManyToManyField(User, through='RSVP', related_name='rsvp_events')

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.name
    
    def get_rsvp_count(self):
        """Get the number of attending RSVPs for this event"""
        return self.rsvp_set.count()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    # Email activation fields
    email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True, null=True)
    email_verification_sent_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_user_role(self):
        """Get the primary role of the user"""
        groups = self.user.groups.all()
        if groups.exists():
            return groups.first().name
        return "No Role"
    
    def is_admin(self):
        return self.user.groups.filter(name='Admin').exists()
    
    def is_organizer(self):
        return self.user.groups.filter(name='Organizer').exists()
    
    def is_participant(self):
        return self.user.groups.filter(name='Participant').exists()

class RSVP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rsvps')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvp_set')
    rsvp_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True, null=True, help_text="Optional notes for the event organizer")
    
    class Meta:
        verbose_name = 'RSVP'
        verbose_name_plural = 'RSVPs'
        unique_together = ['user', 'event']
        ordering = ['-rsvp_date']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name} (Attending)"

class EventRegistration(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='event_registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Event Registration'
        verbose_name_plural = 'Event Registrations'
        unique_together = ['user', 'event']
    
    def __str__(self):
        return f"{self.user.username} - {self.event.name}"