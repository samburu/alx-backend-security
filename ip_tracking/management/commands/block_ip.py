from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP
from django.core.exceptions import ValidationError

class Command(BaseCommand):
    help = 'Add an IP address to the blacklist'

    def add_arguments(self, parser):
        parser.add_argument('ip_address', type=str, help='The IP address to block')

    def handle(self, *args, **options):
        ip_address = options['ip_address']
        try:
            # Validate and save the IP address
            BlockedIP.objects.create(ip_address=ip_address)
            self.stdout.write(self.style.SUCCESS(f'Successfully blocked IP: {ip_address}'))
        except ValidationError as e:
            self.stdout.write(self.style.ERROR(f'Invalid IP address: {ip_address}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error blocking IP {ip_address}: {str(e)}'))