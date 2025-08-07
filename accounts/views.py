from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponse
from django.utils import timezone
from datetime import timedelta
from .forms import UserSignUpForm, UserLoginForm, ProfileEditForm
from .utils import send_activation_email, send_activation_reminder_email
from events.models import UserProfile

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            try:
                # Create user but don't log them in yet
                user = form.save(commit=False)
                user.is_active = True  # Keep user active but unverified
                user.save()
                
                # User profile creation and group assignment will be handled by signals
                
                # Send activation email
                if send_activation_email(user, request):
                    messages.success(request, 'Account created successfully! Please check your email to activate your account before logging in.')
                else:
                    messages.warning(request, 'Account created successfully! However, there was an issue sending the activation email. Please contact support.')
                
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            # Print form errors for debugging
            print("Form errors:", form.errors)
    else:
        form = UserSignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if email is verified
                if hasattr(user, 'profile') and not user.profile.email_verified:
                    messages.error(request, 'Please activate your account by clicking the link in the email we sent you. Check your spam folder if you don\'t see it.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def activate_account(request, uidb64, token):
    """Activate user account using token"""
    try:
        # Decode user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        # Check if user has a profile
        if hasattr(user, 'profile'):
            # Mark email as verified
            user.profile.email_verified = True
            user.profile.email_verification_token = None
            user.profile.save()
            
            messages.success(request, 'Your account has been activated successfully! You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Account activation failed. Please contact support.')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
    
    return redirect('accounts:login')

def resend_activation(request):
    """Resend activation email"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if hasattr(user, 'profile') and not user.profile.email_verified:
                # Check if enough time has passed since last email (prevent spam)
                if (user.profile.email_verification_sent_at is None or 
                    timezone.now() - user.profile.email_verification_sent_at > timedelta(minutes=5)):
                    
                    if send_activation_reminder_email(user, request):
                        messages.success(request, 'Activation email has been resent. Please check your email.')
                    else:
                        messages.error(request, 'Failed to send activation email. Please try again later.')
                else:
                    messages.warning(request, 'Please wait a few minutes before requesting another activation email.')
            else:
                messages.info(request, 'This email is already verified or not found.')
        except User.DoesNotExist:
            messages.info(request, 'No account found with this email address.')
    
    return render(request, 'accounts/resend_activation.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})
