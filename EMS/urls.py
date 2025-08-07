from django.contrib import admin
from django.urls import path, include
from django.db.models import Count
from django.utils.dateparse import parse_date
from events.models import Event, Participant, Category
from django.shortcuts import render

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('events.urls')),
]

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

    total_participants = Participant.objects.count()

    categories = Category.objects.all()  

    return render(request, 'events/event_list.html', {
        'events': events,
        'total_participants': total_participants,
        'categories': categories,
        'selected_category': category_id,
        'start_date': start_date,
        'end_date': end_date,
    })
