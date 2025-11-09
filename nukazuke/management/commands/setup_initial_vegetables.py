from django.core.management.base import BaseCommand
from nukazuke.models import VegetableType


class Command(BaseCommand):
    help = '初期野菜データを作成します'

    def handle(self, *args, **options):
        initial_vegetables = [
            ('きゅうり', '🥒'),
            ('なす', '🍆'),
            ('にんじん', '🥕'),
            ('キャベツ', '🥬'),
            ('ピーマン', '🌶️'),
            ('トマト', '🍅'),
            ('だいこん', '🌶️'),
            ('かぶ', '🌰'),
        ]
        
        created_count = 0
        for name, emoji in initial_vegetables:
            vegetable_type, created = VegetableType.objects.get_or_create(
                name=name,
                defaults={'emoji': emoji}
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'作成: {emoji} {name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'既存: {emoji} {name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'完了: {created_count}個の野菜を新規作成しました')
        )
