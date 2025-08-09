from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone

User = get_user_model()

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
    image = models.ImageField(upload_to='events/', default='events/defaults/default_event.svg', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    rsvp_participants = models.ManyToManyField(User, through='RSVP', related_name='rsvp_events')

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'

    def __str__(self):
        return self.name
    
    def get_rsvp_count(self):
        """Get the number of attending RSVPs for this event"""
        return self.rsvp_set.count()
    
    def has_passed(self):
        """Check if the event date and time has passed"""
        from django.utils import timezone
        import datetime
        
        # Combine date and time to create a datetime object
        event_datetime = datetime.datetime.combine(self.date, self.time)
        # Make it timezone aware
        event_datetime = timezone.make_aware(event_datetime)
        
        return timezone.now() > event_datetime
    
    def can_rsvp(self):
        """Check if users can still RSVP to this event"""
        return not self.has_passed()
    
    def get_absolute_url(self):
        """Get the absolute URL for this event"""
        from django.urls import reverse
        return reverse('event_detail', kwargs={'pk': self.pk})

class UserProfile(models.Model):
    """Legacy UserProfile model for backward compatibility"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s profile"
    
    def get_user_role(self):
        """Get the primary role of the user"""
        return self.user.get_user_role()
    
    def is_admin(self):
        return self.user.is_admin()
    
    def is_organizer(self):
        return self.user.is_organizer()
    
    def is_participant(self):
        return self.user.is_participant()
    
    @property
    def phone(self):
        return self.user.phone_number
    
    @property
    def address(self):
        return self.user.address
    
    @property
    def bio(self):
        return self.user.bio
    
    @property
    def email_verified(self):
        return self.user.email_verified
    
    @property
    def email_verification_token(self):
        return self.user.email_verification_token
    
    @property
    def email_verification_sent_at(self):
        return self.user.email_verification_sent_at

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