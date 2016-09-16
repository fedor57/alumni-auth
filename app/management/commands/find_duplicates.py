from django.core.management.base import BaseCommand
from collections import defaultdict

from app.models import alumni as Alumnus


class Command(BaseCommand):
    help = 'Finds duplicates and clears them'

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Delete duplicates')

    def handle(self, *args, **kwargs):
        delete = kwargs['delete']
        everyone = defaultdict(list)
        for alumnus in Alumnus.objects.all():
            everyone[alumnus.full_name + str(alumnus.year)].append(alumnus)

        for duplicates in everyone.values():
            if len(duplicates) > 1:
                print("Found duplicate:")
                for alumnus in duplicates:
                    print(" " * 4 + unicode(alumnus))

