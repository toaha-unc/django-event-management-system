from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from django.utils import timezone
from django.template.loader import render_to_string
from django.http import HttpResponse
from functools import wraps

from .models import Event, Participant, Category
from .forms import EventForm, ParticipantForm, CategoryForm

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
    events = Event.objects.select_related('category').prefetch_related('participants')
    if query:
        events = events.filter(Q(name__icontains=query) | Q(location__icontains=query))
    return render(request, 'events/home.html', {
        'events': events.order_by('date'),
        'search_query': query
    })

@login_required
def organizer_dashboard(request):
    request.session['from_dashboard'] = True
    today = timezone.now().date()
    all_events = Event.objects.all()
    context = {
        'total_events': all_events.count(),
        'upcoming_events': all_events.filter(date__gt=today).count(),
        'past_events': all_events.filter(date__lt=today).count(),
        'total_participants': Participant.objects.distinct().count(),
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
    events = Event.objects.select_related('category').prefetch_related('participants').all()
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

    total_participants = Participant.objects.filter(events__in=events).distinct().count()
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

@login_required
@dashboard_only
def event_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Event created successfully!")
        return redirect('event_list')
    return render_dashboard(request, 'events/event_form.html', {'form': form})

@login_required
@dashboard_only
def event_update(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, "Event updated successfully!")
        return redirect('event_list')
    return render_dashboard(request, 'events/event_form.html', {'form': form})

@login_required
@dashboard_only
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, "Event deleted successfully!")
        return redirect('event_list')
    return render_dashboard(request, 'events/event_confirm_delete.html', {'event': event})

def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('category').prefetch_related('participants'), pk=pk)
    context = {'event': event}
    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/event_detail.html', context)
    return render(request, 'events/event_detail.html', context)

def participant_list(request):
    context = {'participants': Participant.objects.all()}
    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/participant_list.html', context)
    return render(request, 'events/participant_list.html', context)

@login_required
@dashboard_only
def participant_create(request):
    if not Event.objects.exists():
        messages.error(request, "Cannot add participant because there are no events available.")
        return redirect('event_list')
    form = ParticipantForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Participant added successfully!")
        return redirect('participant_list')
    return render_dashboard(request, 'events/participant_form.html', {'form': form})

@login_required
@dashboard_only
def participant_update(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    form = ParticipantForm(request.POST or None, instance=participant)
    if form.is_valid():
        form.save()
        messages.success(request, "Participant updated successfully!")
        return redirect('participant_list')
    return render_dashboard(request, 'events/participant_form.html', {'form': form})

@login_required
@dashboard_only
def participant_delete(request, pk):
    participant = get_object_or_404(Participant, pk=pk)
    if request.method == 'POST':
        participant.delete()
        messages.success(request, "Participant deleted successfully!")
        return redirect('participant_list')
    return render_dashboard(request, 'events/participant_confirm_delete.html', {'participant': participant})

def category_list(request):
    context = {'categories': Category.objects.all()}
    if request.session.get('from_dashboard'):
        return render_dashboard(request, 'events/category_list.html', context)
    return render(request, 'events/category_list.html', context)

@login_required
@dashboard_only
def category_create(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Category created successfully!")
        return redirect('category_list')
    return render_dashboard(request, 'events/category_form.html', {'form': form})

@login_required
@dashboard_only
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=category)
    if form.is_valid():
        form.save()
        messages.success(request, "Category updated successfully!")
        return redirect('category_list')
    return render_dashboard(request, 'events/category_form.html', {'form': form})

@login_required
@dashboard_only
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, "Category deleted successfully!")
        return redirect('category_list')
    return render_dashboard(request, 'events/category_confirm_delete.html', {'category': category})
