from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Creates or updates the Site object for kwc1.barocay.com'

    def handle(self, *args, **options):
        site_id = 2
        domain = 'kwc1.barocay.com'
        name = 'KWC1 Barocay'

        site, created = Site.objects.update_or_create(
            id=site_id,
            defaults={
                'domain': domain,
                'name': name
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Successfully created site: {site}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated site: {site}'))
