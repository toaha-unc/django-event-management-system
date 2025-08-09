from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetConfirmView
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.http import HttpResponse
from django.utils import timezone
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView
from datetime import timedelta
from .forms import UserSignUpForm, UserLoginForm, ProfileEditForm, CustomPasswordChangeForm
from .utils import send_activation_email, send_activation_reminder_email

User = get_user_model()

def signup_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin() or request.user.is_organizer():
            return redirect('organizer_dashboard')
        else:
            return redirect('participant_dashboard')
    
    if request.method == 'POST':
        form = UserSignUpForm(request.POST)
        if form.is_valid():
            try:
                
                user = form.save(commit=False)
                user.is_active = True  
                user.save()
                

                if send_activation_email(user, request):
                    messages.success(request, 'Account created successfully! Please check your email to activate your account before logging in.')
                else:
                    messages.warning(request, 'Account created successfully! However, there was an issue sending the activation email. Please contact support.')
                
                return redirect('accounts:login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
            
            print("Form errors:", form.errors)
    else:
        form = UserSignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_admin() or request.user.is_organizer():
            return redirect('organizer_dashboard')
        else:
            return redirect('participant_dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                
                if not user.email_verified:
                    messages.error(request, 'Please activate your account by clicking the link in the email we sent you. Check your spam folder if you don\'t see it.')
                    return render(request, 'accounts/login.html', {'form': form})
                
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                
                
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                

                if user.is_admin():
                    return redirect('organizer_dashboard')  
                elif user.is_organizer():
                    return redirect('organizer_dashboard')
                else: 
                    return redirect('participant_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def activate_account(request, uidb64, token):
    
    try:
        
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        user.email_verified = True
        user.email_verification_token = None
        user.save()
        
        messages.success(request, 'Your account has been activated successfully! You can now log in.')
        return redirect('accounts:login')
    else:
        messages.error(request, 'The activation link is invalid or has expired.')
    
    return redirect('accounts:login')

def resend_activation(request):
    
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.email_verified:
                
                if (user.email_verification_sent_at is None or 
                    timezone.now() - user.email_verification_sent_at > timedelta(minutes=5)):
                    
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
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'accounts/profile_edit.html', {'form': form})

# Class-based views for enhanced profile features
class ProfileView(LoginRequiredMixin, TemplateView):
    """Class-based view for displaying user profile"""
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Class-based view for editing user profile"""
    form_class = ProfileEditForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Class-based view for changing password"""
    form_class = CustomPasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

class CustomPasswordResetView(PasswordResetView):
    """Class-based view for password reset"""
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/emails/password_reset_email.html'
    subject_template_name = 'accounts/emails/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    
    def form_valid(self, form):
        messages.success(self.request, 'Password reset email has been sent!')
        return super().form_valid(form)

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Class-based view for password reset confirmation"""
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been reset successfully!')
        return super().form_valid(form)
