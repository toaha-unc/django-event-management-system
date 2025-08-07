from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User

class EmailActivationBackend(ModelBackend):
    """
    Custom authentication backend that prevents unactivated users from logging in
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        
        if user is not None:
            if hasattr(user, 'profile'):
                if not user.profile.email_verified:
                    return None
            
        return user
