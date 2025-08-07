from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

class Command(BaseCommand):
    help = 'Assign superuser to Admin group'

    def handle(self, *args, **options):
        try:
            # Get the superuser
            superuser = User.objects.filter(is_superuser=True).first()
            if not superuser:
                self.stdout.write(
                    self.style.ERROR('No superuser found. Please create a superuser first.')
                )
                return

            # Get or create Admin group
            admin_group, created = Group.objects.get_or_create(name='Admin')
            
            # Add superuser to Admin group
            superuser.groups.add(admin_group)
            
            # Create user profile if it doesn't exist
            from events.models import UserProfile
            UserProfile.objects.get_or_create(user=superuser)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully assigned {superuser.username} to Admin group'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error: {e}')
            )
