from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from events.models import Event, Category, UserProfile, EventRegistration, RSVP

class Command(BaseCommand):
    help = 'Set up initial user groups and permissions for the event management system'

    def handle(self, *args, **options):
        admin_group, created = Group.objects.get_or_create(name='Admin')
        organizer_group, created = Group.objects.get_or_create(name='Organizer')
        participant_group, created = Group.objects.get_or_create(name='Participant')

        event_ct = ContentType.objects.get_for_model(Event)
        category_ct = ContentType.objects.get_for_model(Category)
        userprofile_ct = ContentType.objects.get_for_model(UserProfile)
        eventregistration_ct = ContentType.objects.get_for_model(EventRegistration)
        rsvp_ct = ContentType.objects.get_for_model(RSVP)

        event_permissions = Permission.objects.filter(content_type=event_ct)
        category_permissions = Permission.objects.filter(content_type=category_ct)
        userprofile_permissions = Permission.objects.filter(content_type=userprofile_ct)
        eventregistration_permissions = Permission.objects.filter(content_type=eventregistration_ct)
        rsvp_permissions = Permission.objects.filter(content_type=rsvp_ct)

        admin_group.permissions.set(
            list(event_permissions) + 
            list(category_permissions) + 
            list(userprofile_permissions) + 
            list(eventregistration_permissions) +
            list(rsvp_permissions)
        )

        organizer_permissions = []
        for perm in event_permissions:
            organizer_permissions.append(perm)
        for perm in category_permissions:
            organizer_permissions.append(perm)
        for perm in rsvp_permissions:
            organizer_permissions.append(perm)
        
        organizer_group.permissions.set(organizer_permissions)

        participant_permissions = []
        for perm in event_permissions:
            if perm.codename == 'view_event':
                participant_permissions.append(perm)
        for perm in category_permissions:
            if perm.codename == 'view_category':
                participant_permissions.append(perm)
        for perm in rsvp_permissions:
            if perm.codename in ['add_rsvp', 'change_rsvp', 'delete_rsvp', 'view_rsvp']:
                participant_permissions.append(perm)
        
        participant_group.permissions.set(participant_permissions)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created groups:\n'
                f'- Admin: {admin_group.permissions.count()} permissions\n'
                f'- Organizer: {organizer_group.permissions.count()} permissions\n'
                f'- Participant: {participant_group.permissions.count()} permissions'
            )
        )
