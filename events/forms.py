from django import forms
from .models import Event, Participant, Category

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
            'name': forms.TextInput(attrs={'class': tailwind_input_class}),
            'description': forms.Textarea(attrs={'class': tailwind_input_class}),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'placeholder': 'YYYY-MM-DD',
                'class': tailwind_input_class
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'placeholder': 'HH:MM',
                'class': tailwind_input_class
            }),
            'location': forms.TextInput(attrs={'class': tailwind_input_class}),
            'category': forms.Select(attrs={'class': tailwind_input_class}),
        }

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'email', 'events']
        widgets = {
            'name': forms.TextInput(attrs={'class': tailwind_input_class}),
            'email': forms.EmailInput(attrs={'class': tailwind_input_class}),
            'events': forms.CheckboxSelectMultiple(attrs={'class': 'space-y-2'})
        }

    def clean_events(self):
        events = self.cleaned_data.get('events')
        if not events or events.count() == 0:
            raise forms.ValidationError("You must select at least one event.")
        return events
