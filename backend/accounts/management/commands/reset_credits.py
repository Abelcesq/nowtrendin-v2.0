from django.core.management.base import BaseCommand
from accounts.credits import reset_all_credits


class Command(BaseCommand):
    help = "Reset every profile's monthly query + AI-grade credits to its tier allowance."

    def handle(self, *args, **options):
        counts = reset_all_credits()
        self.stdout.write(self.style.SUCCESS(f"Credits reset: {counts}"))
