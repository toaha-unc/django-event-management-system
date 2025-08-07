from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.contrib.auth.models import Group

def role_required(allowed_roles):
    """
    Decorator to check if user has any of the specified roles.
    allowed_roles: list of role names (group names)
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            

            user_groups = request.user.groups.all()
            user_role_names = [group.name for group in user_groups]
            
            if not any(role in user_role_names for role in allowed_roles):
                messages.error(request, f"You don't have permission to access this page. Required roles: {', '.join(allowed_roles)}")
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """Decorator to check if user has admin role"""
    return role_required(['Admin'])(view_func)

def organizer_required(view_func):
    """Decorator to check if user has organizer role"""
    return role_required(['Organizer'])(view_func)

def admin_or_organizer_required(view_func):
    """Decorator to check if user has admin or organizer role"""
    return role_required(['Admin', 'Organizer'])(view_func)

def participant_required(view_func):
    """Decorator to check if user has participant role"""
    return role_required(['Participant'])(view_func)

def any_authenticated_user(view_func):
    """Decorator to check if user is authenticated (any role)"""
    return login_required(view_func)
