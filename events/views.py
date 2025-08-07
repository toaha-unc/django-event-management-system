from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from functools import wraps
from django.contrib.auth.models import User, Group

from .models import Event, Category, UserProfile, EventRegistration
from .forms import EventForm, CategoryForm
from accounts.decorators import (
    admin_required, organizer_required, admin_or_organizer_required,
    participant_required, any_authenticated_user
)

def render_dashboard(request, template, context):
    if request.session.get('from_dashboard'):
        context['active_page'] = 'dashboard'
    return render(request, template, context)

def dashboard_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('from_dashboard'):
            messages.error(request, "You can only perform this action from the Organizer Dashboard.")
            return redirect('event_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def home(request):
    request.session.pop('from_dashboard', None)  # Exit dashboard mode
    query = request.GET.get('search', '')
    events = Event.objects.select_related('category').prefetch_related('registrations')
    if query:
        events = events.filter(Q(name__icontains=query) | Q(location__icontains=query))
    return render(request, 'events/home.html', {
        'events': events.order_by('date'),
        'search_query': query
    })

@admin_or_organizer_required
def organizer_dashboard(request):
    request.session['from_dashboard'] = True
    today = timezone.now().date()
    all_events = Event.objects.all()
    context = {
        'total_events': all_events.count(),
        'upcoming_events': all_events.filter(date__gt=today).count(),
        'past_events': all_events.filter(date__lt=today).count(),
        'total_participants': User.objects.filter(groups__name='Participant').count(),
        'todays_events': all_events.filter(date=today),
    }

    stats_type = request.GET.get('stats')
    if stats_type:
        if stats_type == 'total':
            context.update({'stats_type': 'total', 'all_events': all_events})
        elif stats_type == 'upcoming':
            context.update({'stats_type': 'upcoming', 'upcoming_events_list': all_events.filter(date__gt=today)})
        elif stats_type == 'past':
            context.update({'stats_type': 'past', 'past_events_list': all_events.filter(date__lt=today)})
        return HttpResponse(render_to_string('events/_stats_content.html', context, request))

    return render_dashboard(request, 'events/organizer_dashboard.html', context)

def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('registrations').all()
    category_id = request.GET.get('category')
    if category_id:
        events = events.filter(category_id=category_id)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        events = events.filter(date__range=[start_date, end_date])
    elif start_date:
        events = events.filter(date__gte=start_date)
    elif end_date:
        events = events.filter(date__lte=end_date)

    total_participants = User.objects.filter(groups__name='Participant').count()
    categories = Category.objects.all()

    context = {
        'events': events,
        'total_participants': total_participants,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    }

    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/event_list.html', context)
    return render(request, 'events/event_list.html', context)

@admin_or_organizer_required
@dashboard_only
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        event = form.save(commit=False)
        event.created_by = request.user
        event.save()
        messages.success(request, "Event created successfully!")
        return redirect('event_list')
    return render_dashboard(request, 'events/event_form.html', {'form': form})

@admin_or_organizer_required
@dashboard_only
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, "Event updated successfully!")
        return redirect('event_list')
    return render_dashboard(request, 'events/event_form.html', {'form': form})

@admin_or_organizer_required
@dashboard_only
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('event_list')
    return render_dashboard(request, 'events/event_confirm_delete.html', {'event': event})

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('registrations'), pk=pk)
    context = {'event': event}
    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/event_detail.html', context)
    return render(request, 'events/event_detail.html', context)

@admin_required
def user_list(request):
    participants = User.objects.filter(groups__name='Participant')
    organizers = User.objects.filter(groups__name='Organizer')
    admins = User.objects.filter(groups__name='Admin')
    
    context = {
        'participants': participants,
        'organizers': organizers,
        'admins': admins,
    }
    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/user_list.html', context)
    return render(request, 'events/user_list.html', context)

@admin_required
@dashboard_only
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, "User deleted successfully!")
        return redirect('user_list')
    return render_dashboard(request, 'events/user_confirm_delete.html', {'user': user})

@admin_required
@dashboard_only
def user_role_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['Admin', 'Organizer', 'Participant']:
            # Remove from all groups
            user.groups.clear()
            # Add to new group
            group, created = Group.objects.get_or_create(name=new_role)
            user.groups.add(group)
            messages.success(request, f"User role updated to {new_role} successfully!")
        else:
            messages.error(request, "Invalid role selected.")
        return redirect('user_list')
    
    current_role = user.groups.first().name if user.groups.exists() else 'No Role'
    context = {
        'user': user,
        'current_role': current_role,
        'available_roles': ['Admin', 'Organizer', 'Participant']
    }
    return render_dashboard(request, 'events/user_role_form.html', context)

def category_list(request):
    context = {'categories': Category.objects.all()}
    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/category_list.html', context)
    return render(request, 'events/category_list.html', context)

@admin_or_organizer_required
@dashboard_only
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category created successfully!")
        return redirect('category_list')
    return render_dashboard(request, 'events/category_form.html', {'form': form})

@admin_or_organizer_required
@dashboard_only
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully!")
        return redirect('category_list')
    return render_dashboard(request, 'events/category_form.html', {'form': form})

@admin_or_organizer_required
@dashboard_only
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect('category_list')
    return render_dashboard(request, 'events/category_confirm_delete.html', {'category': category})

@any_authenticated_user
def register_for_event(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if request.method == 'POST':
        registration, created = EventRegistration.objects.get_or_create(
            user=request.user,
            event=event
        )
        if created:
            messages.success(request, f"Successfully registered for {event.name}!")
        else:
            messages.info(request, f"You are already registered for {event.name}.")
        return redirect('event_detail', pk=event_pk)
    
    return redirect('event_detail', pk=event_pk)

@any_authenticated_user
def unregister_from_event(request, event_pk):
    event = get_object_or_404(Event, pk=event_pk)
    if request.method == 'POST':
        try:
            registration = EventRegistration.objects.get(user=request.user, event=event)
            registration.delete()
            messages.success(request, f"Successfully unregistered from {event.name}!")
        except EventRegistration.DoesNotExist:
            messages.error(request, f"You are not registered for {event.name}.")
        return redirect('event_detail', pk=event_pk)
    
    return redirect('event_detail', pk=event_pk)
