from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class CustomUserAdmin(UserAdmin):
    """Admin interface for CustomUser model"""
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'phone_number', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'email_verified', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    # Add custom fields to the form
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'bio', 'address', 'profile_picture', 'email_verified')
        }),
    )
    
    # Add custom fields to the add form
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('phone_number', 'bio', 'address', 'profile_picture')
        }),
    )

class UserProfileAdmin(admin.ModelAdmin):
    """Admin interface for UserProfile model (legacy compatibility)"""
    list_display = ['user', 'get_phone', 'get_email_verified', 'get_user_role']
    search_fields = ['user__username', 'user__email']
    
    def get_phone(self, obj):
        return obj.user.phone_number  # Access through the actual CustomUser field
    get_phone.short_description = 'Phone Number'
    
    def get_email_verified(self, obj):
        return obj.user.email_verified  # Access through the actual CustomUser field
    get_email_verified.short_description = 'Email Verified'
    get_email_verified.boolean = True
    
    def get_user_role(self, obj):
        return obj.get_user_role()
    get_user_role.short_description = 'Role'

# Register the models
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
