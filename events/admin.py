from django.contrib import admin
from .models import Event, Category, UserProfile, EventRegistration

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['name', 'date', 'time', 'location', 'category', 'created_by', 'created_at']
    list_filter = ['category', 'date', 'created_at']
    search_fields = ['name', 'description', 'location']
    date_hierarchy = 'date'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'get_user_role']
    search_fields = ['user__username', 'user__email']
    list_filter = ['user__groups__name']

    def get_user_role(self, obj):
        return obj.get_user_role()
    get_user_role.short_description = 'Role'

@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'event', 'registered_at', 'attended']
    list_filter = ['attended', 'registered_at', 'event__category']
    search_fields = ['user__username', 'event__name']
    date_hierarchy = 'registered_at'
