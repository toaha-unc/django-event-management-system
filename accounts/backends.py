from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class EmailActivationBackend(ModelBackend):
    """
    Custom authentication backend that prevents unactivated users from logging in
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)
        
        if user is not None:
            # Check email verification directly on the CustomUser model
            if not user.email_verified:
                return None
            
        return user
