from django.core.management.base import BaseCommand
from django.conf import settings

from app.models import alumni as Alumnus


class Command(BaseCommand):
    help = 'Loads alumni from data/alumni-db.tsv'

    def handle(self, *args, **kwargs):
        with open(settings.BASE_DIR + '/data/alumni-db.tsv') as f:
            for line in f:
                full_name, year, letter = line.strip().split('\t')
                a = Alumnus(full_name=full_name, year=int(year), letter=letter)
                a.added_by = 'import'
                a.save()


