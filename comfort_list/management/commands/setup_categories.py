from django.core.management.base import BaseCommand
from comfort_list.models import Category

class Command(BaseCommand):
    help = '心地よさのカテゴリ初期データを作成します'

    def handle(self, *args, **options):
        categories_data = [
            ('heart', '心', '🌱'),
            ('body', '体', '🍔'),
            ('space', '空間', '🏠'),
            ('time', '時間', '⏰'),
            ('mind', '頭', '💡'),
            ('relationship', '人間関係', '🧸'),
            ('hobby', '好きなこと', '🌻'),
            ('self', '自分', '💝'),
        ]
        
        created_count = 0
        updated_count = 0
        for name, display_name, emoji in categories_data:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'emoji': emoji
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'カテゴリ "{emoji} {display_name}" を作成しました')
                )
            else:
                # 既存のカテゴリの絵文字を更新
                if category.emoji != emoji or category.display_name != display_name:
                    old_emoji = category.emoji
                    category.emoji = emoji
                    category.display_name = display_name
                    category.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'カテゴリ "{old_emoji} → {emoji} {display_name}" を更新しました')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'カテゴリ "{emoji} {display_name}" は既に最新です')
                    )
        
        if created_count > 0 or updated_count > 0:
            if created_count > 0 and updated_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✨ {created_count} 個のカテゴリを作成、{updated_count} 個のカテゴリを更新しました！')
                )
            elif created_count > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✨ 合計 {created_count} 個のカテゴリを作成しました！')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'🔄 合計 {updated_count} 個のカテゴリを更新しました！')
                )
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ 全てのカテゴリが既に最新です！')
            ) 