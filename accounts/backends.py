from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailActivationBackend(ModelBackend):
    """
    Custom authentication backend that prevents unactivated users from logging in
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # First, try to authenticate normally
        user = super().authenticate(request, username, password, **kwargs)
        
        if user is not None:
            # Check if user has a profile and if email is verified
            if hasattr(user, 'profile'):
                if not user.profile.email_verified:
                    # Return None to prevent login for unverified users
                    return None
            
        return user
