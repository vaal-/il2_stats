import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import Object, Score


class Command(BaseCommand):
    def handle(self, *args, **options):
        base_dir = settings.BASE_DIR
        score = base_dir.joinpath('score.csv')
        score_dict = {}
        with score.open(encoding='utf-8') as file_csv:
            for row in csv.DictReader(file_csv):
                s = Score.objects.update_or_create(key=row['key'].lower(),
                                                   defaults={'type': row['type'], 'value': row['value']})[0]
                score_dict[s.key] = s.id

        objects = base_dir.joinpath('objects.csv')
        with objects.open(encoding='utf-8') as file_csv:
            for row in csv.DictReader(file_csv):
                name_en = row['name'] or row['log_name']
                is_playable = bool(int(row['playable']))
                Object.objects.update_or_create(log_name=row['log_name'].lower(),
                                                defaults={'name': name_en, 'name_en': name_en, 'name_ru': row['name_ru'],
                                                          'score_id': score_dict[row['cls']], 'is_playable': is_playable,
                                                          'cls': row['cls']})
        classes = base_dir.joinpath('classes.csv')
        with classes.open(encoding='utf-8') as file_csv:
            for row in csv.DictReader(file_csv):
                Object.objects.filter(cls=row['cls']).update(cls_base=row['cls_base'])
