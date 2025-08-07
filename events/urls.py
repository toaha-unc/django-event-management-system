from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_update, name='category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/<int:pk>/edit/', views.event_update, name='event_update'),
    path('events/<int:pk>/delete/', views.event_delete, name='event_delete'),
    path('events/<int:pk>/', views.event_detail, name='event_detail'),
    path('events/<int:event_pk>/register/', views.register_for_event, name='register_for_event'),
    path('events/<int:event_pk>/unregister/', views.unregister_from_event, name='unregister_from_event'),
    
    
    path('events/<int:event_pk>/rsvp/', views.rsvp_create, name='rsvp_create'),
    path('events/<int:event_pk>/rsvp/delete/', views.rsvp_delete, name='rsvp_delete'),

    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:pk>/role/', views.user_role_update, name='user_role_update'),

    path('dashboard/', views.organizer_dashboard, name='organizer_dashboard'),
    path('participant-dashboard/', views.participant_dashboard, name='participant_dashboard'),
]
