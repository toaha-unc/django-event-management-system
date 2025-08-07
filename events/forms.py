from django import forms
from .models import Event, Category, UserProfile, RSVP

tailwind_input_class = (
    'w-full px-3 py-2 border border-gray-300 rounded-sm '
    'focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-300'
)

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': tailwind_input_class}),
            'description': forms.Textarea(attrs={'class': tailwind_input_class}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'description', 'date', 'time', 'location', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter event name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Enter event description'
            }),
            'date': forms.DateInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'time': forms.TimeInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'time'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter event location'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            })
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone', 'address', 'bio']
        widgets = {
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Enter your phone number'
            }),
            'address': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Enter your address'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Tell us about yourself'
            })
        }

class RSVPForm(forms.ModelForm):
    class Meta:
        model = RSVP
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Optional: Add any notes for the event organizer'
            })
        }
