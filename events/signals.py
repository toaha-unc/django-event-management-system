from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from .models import RSVP, UserProfile
from .utils import send_rsvp_confirmation_email, send_rsvp_update_email
from accounts.utils import send_activation_email

# User profile creation is handled in accounts/signals.py to avoid conflicts

@receiver(post_save, sender=RSVP)
def send_rsvp_notification(sender, instance, created, **kwargs):
    """Send email notification when user RSVPs to an event"""
    if created:
        # Send RSVP confirmation email
        send_rsvp_confirmation_email(instance.user, instance.event)
    else:
        # Send RSVP update email
        send_rsvp_update_email(instance.user, instance.event)

@receiver(post_delete, sender=RSVP)
def send_rsvp_cancellation(sender, instance, **kwargs):
    """Send email notification when user cancels RSVP"""
    from django.core.mail import send_mail
    from django.conf import settings
    from django.template.loader import render_to_string
    
    subject = f'RSVP Cancelled for {instance.event.name}'
    
    context = {
        'user': instance.user,
        'event': instance.event,
    }
    
    # Render HTML email
    html_message = render_to_string('events/emails/rsvp_cancelled.html', context)
    
    # Render plain text email
    plain_message = render_to_string('events/emails/rsvp_cancelled.txt', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending RSVP cancellation email: {e}")
