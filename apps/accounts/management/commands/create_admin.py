from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _


class Command(BaseCommand):
    help = _('Create super user for application')

    def handle(self, *args, **options):

        User = get_user_model()

        if not User.objects.filter(email='admin.admin.com').exists():
            User.objects.create_superuser(
                email='admin@admin.com',
                password='admin',
                username='admin'
            )
            self.stdout.write(self.style.SUCCESS('Successfully created superuser'))
        else:
            self.stdout.write(self.style.SUCCESS('Superuser already exists!!'))
