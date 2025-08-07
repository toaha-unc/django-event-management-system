from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from functools import wraps
from django.contrib.auth.models import User, Group

from .models import Event, Category, UserProfile, EventRegistration, RSVP
from .forms import EventForm, CategoryForm, RSVPForm
from accounts.decorators import (
    admin_required, organizer_required, admin_or_organizer_required,
    participant_required, any_authenticated_user
)
from .utils import send_rsvp_confirmation_email, send_rsvp_update_email

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
    
    # Count active participants (unique users who have RSVP'd)
    total_participants = User.objects.filter(rsvps__isnull=False).distinct().count()
    
    context = {
        'total_events': all_events.count(),
        'upcoming_events': all_events.filter(date__gt=today).count(),
        'past_events': all_events.filter(date__lt=today).count(),
        'total_participants': total_participants,
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
        elif stats_type == 'participants':
            # Get only users who have RSVP'd to events
            users_with_rsvps = User.objects.filter(rsvps__isnull=False).distinct().order_by('first_name', 'last_name', 'username')
            
            context.update({
                'stats_type': 'participants',
                'users_with_rsvps': users_with_rsvps,
            })
        return HttpResponse(render_to_string('events/_stats_content.html', context, request))

    return render_dashboard(request, 'events/organizer_dashboard.html', context)

@any_authenticated_user
def participant_dashboard(request):
    """Dashboard for participants to view their RSVPs"""
    user = request.user
    user_rsvps = RSVP.objects.filter(user=user).select_related('event', 'event__category').order_by('event__date')
    
    # Separate RSVPs by status
    upcoming_rsvps = user_rsvps.filter(event__date__gte=timezone.now().date())
    past_rsvps = user_rsvps.filter(event__date__lt=timezone.now().date())
    
    context = {
        'upcoming_rsvps': upcoming_rsvps,
        'past_rsvps': past_rsvps,
        'total_rsvps': user_rsvps.count(),
    }
    
    return render(request, 'events/participant_dashboard.html', context)

def event_list(request):
    events = Event.objects.select_related('category').prefetch_related('rsvp_set__user').all()
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

    # Count participants based on RSVPs
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
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully!')
            return redirect('event_list')
    else:
        form = EventForm()
    
    return render_dashboard(request, 'events/event_form.html', {'form': form, 'title': 'Create Event'})

@admin_or_organizer_required
@dashboard_only
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully!')
            return redirect('event_list')
    else:
        form = EventForm(instance=event)
    
    return render_dashboard(request, 'events/event_form.html', {'form': form, 'title': 'Edit Event'})

@admin_or_organizer_required
@dashboard_only
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully!')
        return redirect('event_list')
    
    return render_dashboard(request, 'events/event_confirm_delete.html', {'event': event})

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    user_rsvp = None
    
    if request.user.is_authenticated:
        user_rsvp = RSVP.objects.filter(user=request.user, event=event).first()
    
    # Get RSVP statistics
    rsvp_stats = {
        'total_rsvps': event.get_rsvp_count(),
    }
    
    context = {
        'event': event,
        'user_rsvp': user_rsvp,
        'rsvp_stats': rsvp_stats,
    }
    
    return render(request, 'events/event_detail.html', context)

@admin_required
def user_list(request):
    # Get all users with their roles and RSVP counts
    users = User.objects.select_related('profile').prefetch_related('groups', 'rsvps').all()
    
    # Add additional context for each user
    for user in users:
        user.rsvp_count = user.rsvps.count()
        user.primary_role = user.groups.first().name if user.groups.exists() else 'No Role'
    
    # Calculate role counts
    admin_count = sum(1 for user in users if user.primary_role == 'Admin')
    organizer_count = sum(1 for user in users if user.primary_role == 'Organizer')
    participant_count = sum(1 for user in users if user.primary_role == 'Participant')
    
    context = {
        'users': users,
        'admin_count': admin_count,
        'organizer_count': organizer_count,
        'participant_count': participant_count,
    }
    
    return render(request, 'events/user_list.html', context)

@admin_required
@dashboard_only
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('user_list')
    
    return render_dashboard(request, 'events/user_confirm_delete.html', {'user': user})

@admin_required
@dashboard_only
def user_role_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        role = request.POST.get('role')
        if role:
            # Remove user from all groups
            user.groups.clear()
            # Add user to selected group
            group = Group.objects.get(name=role)
            user.groups.add(group)
            messages.success(request, f'User role updated to {role}')
            return redirect('user_list')
    
    # Get current role and available roles
    current_role = user.groups.first().name if user.groups.exists() else 'No Role'
    available_roles = ['Admin', 'Organizer', 'Participant']
    
    context = {
        'user': user,
        'current_role': current_role,
        'available_roles': available_roles,
    }
    
    return render_dashboard(request, 'events/user_role_form.html', context)

def category_list(request):
    categories = Category.objects.prefetch_related('events').all()
    return render(request, 'events/category_list.html', {'categories': categories})

@admin_or_organizer_required
@dashboard_only
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render_dashboard(request, 'events/category_form.html', {'form': form, 'title': 'Create Category'})

@admin_or_organizer_required
@dashboard_only
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render_dashboard(request, 'events/category_form.html', {'form': form, 'title': 'Edit Category'})

@admin_or_organizer_required
@dashboard_only
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    
    return render_dashboard(request, 'events/category_confirm_delete.html', {'category': category})

@any_authenticated_user
def rsvp_create(request, event_pk):
    """Create or update RSVP for an event"""
    event = get_object_or_404(Event, pk=event_pk)
    user = request.user
    
    # Check if user already has an RSVP for this event
    existing_rsvp = RSVP.objects.filter(user=user, event=event).first()
    
    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=existing_rsvp)
        if form.is_valid():
            rsvp = form.save(commit=False)
            rsvp.user = user
            rsvp.event = event
            rsvp.save()
            
            # Send email confirmation
            if existing_rsvp:
                # Update email
                send_rsvp_update_email(user, event)
                messages.success(request, 'Your RSVP has been updated!')
            else:
                # New RSVP email
                send_rsvp_confirmation_email(user, event)
                messages.success(request, 'Thank you for your RSVP!')
            
            return redirect('event_detail', pk=event_pk)
    else:
        form = RSVPForm(instance=existing_rsvp)
    
    context = {
        'form': form,
        'event': event,
        'existing_rsvp': existing_rsvp,
    }
    
    return render(request, 'events/rsvp_form.html', context)

@any_authenticated_user
def rsvp_delete(request, event_pk):
    """Delete RSVP for an event"""
    event = get_object_or_404(Event, pk=event_pk)
    user = request.user
    
    try:
        rsvp = RSVP.objects.get(user=user, event=event)
        if request.method == 'POST':
            rsvp.delete()
            messages.success(request, 'Your RSVP has been removed.')
            return redirect('event_detail', pk=event_pk)
    except RSVP.DoesNotExist:
        messages.error(request, 'You do not have an RSVP for this event.')
        return redirect('event_detail', pk=event_pk)
    
    return render(request, 'events/rsvp_confirm_delete.html', {'event': event, 'rsvp': rsvp})

# Legacy registration functions - now redirect to RSVP
@any_authenticated_user
def register_for_event(request, event_pk):
    """Legacy function - redirect to RSVP"""
    messages.info(request, 'Registration has been replaced with RSVP. Please use the RSVP system.')
    return redirect('rsvp_create', event_pk=event_pk)

@any_authenticated_user
def unregister_from_event(request, event_pk):
    """Legacy function - redirect to RSVP deletion"""
    messages.info(request, 'Unregistration has been replaced with RSVP removal. Please use the RSVP system.')
    return redirect('rsvp_delete', event_pk=event_pk)
