from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils import timezone

def send_activation_email(user, request):
    """
    Send activation email to user
    """
    # Generate token
    token = default_token_generator.make_token(user)
    
    # Encode user ID
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create activation URL
    activation_url = request.build_absolute_uri(
        reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Activate Your Account - Event Management System'
    
    # Email template context
    context = {
        'user': user,
        'activation_url': activation_url,
    }
    
    # Render HTML email
    html_message = render_to_string('accounts/emails/activation_email.html', context)
    
    # Render plain text email
    plain_message = render_to_string('accounts/emails/activation_email.txt', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Update user profile with token info
        user.profile.email_verification_token = token
        user.profile.email_verification_sent_at = timezone.now()
        user.profile.save()
        
        return True
    except Exception as e:
        print(f"Error sending activation email: {e}")
        return False

def send_activation_reminder_email(user, request):
    """
    Send activation reminder email to user
    """
    # Generate new token
    token = default_token_generator.make_token(user)
    
    # Encode user ID
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Create activation URL
    activation_url = request.build_absolute_uri(
        reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Activate Your Account - Reminder'
    
    # Email template context
    context = {
        'user': user,
        'activation_url': activation_url,
        'is_reminder': True,
    }
    
    # Render HTML email
    html_message = render_to_string('accounts/emails/activation_email.html', context)
    
    # Render plain text email
    plain_message = render_to_string('accounts/emails/activation_email.txt', context)
    
    # Send email
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Update user profile with new token info
        user.profile.email_verification_token = token
        user.profile.email_verification_sent_at = timezone.now()
        user.profile.save()
        
        return True
    except Exception as e:
        print(f"Error sending activation reminder email: {e}")
        return False
