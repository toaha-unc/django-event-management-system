from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import RSVP

def send_rsvp_confirmation_email(user, event):
    """
    Send RSVP confirmation email to user
    """
    subject = f'RSVP Confirmation for {event.name}'
    
    
    context = {
        'user': user,
        'event': event,
    }
    
    
    html_message = render_to_string('events/emails/rsvp_confirmation.html', context)
    
    
    plain_message = render_to_string('events/emails/rsvp_confirmation.txt', context)
    
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending RSVP confirmation email: {e}")
        return False

def send_rsvp_update_email(user, event):
    """
    Send RSVP update email to user
    """
    subject = f'RSVP Updated for {event.name}'
    
    
    context = {
        'user': user,
        'event': event,
    }
    
    
    html_message = render_to_string('events/emails/rsvp_update.html', context)
    
    
    plain_message = render_to_string('events/emails/rsvp_update.txt', context)
    
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending RSVP update email: {e}")
        return False
