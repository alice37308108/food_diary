from django.core.management.base import BaseCommand
from django.utils import timezone
from nukazuke.models import PickledVegetable
from nukazuke.views import send_line_message
import sys
import io


class Command(BaseCommand):
    help = 'ぬか漬けのリマインドメッセージを送信します'

    def handle(self, *args, **options):
        # Windows環境でのUTF-8出力対応
        if sys.platform == 'win32':
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        now = timezone.now()
        sent_count = 0
        
        # 現在漬けている野菜を取得
        pickled_vegetables = PickledVegetable.objects.filter(removed_at__isnull=True)
        
        for vegetable in pickled_vegetables:
            hours_elapsed = vegetable.hours_pickled
            
            # 72時間経過でまだ送信していない場合（優先度高）
            if (hours_elapsed >= 72 and not vegetable.reminder_72h_sent):
                if send_line_message(vegetable.id):
                    sent_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'72時間リマインド送信: {vegetable.display_name} ({hours_elapsed:.1f}時間経過)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'72時間リマインド送信失敗: {vegetable.display_name}'
                        )
                    )
            
            # 48時間経過でまだ送信していない場合
            elif (hours_elapsed >= 48 and not vegetable.reminder_48h_sent):
                if send_line_message(vegetable.id):
                    sent_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'48時間リマインド送信: {vegetable.display_name} ({hours_elapsed:.1f}時間経過)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'48時間リマインド送信失敗: {vegetable.display_name}'
                        )
                    )
            
            # 24時間経過でまだ送信していない場合
            elif (hours_elapsed >= 24 and not vegetable.reminder_24h_sent):
                if send_line_message(vegetable.id):
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'24時間リマインド送信: {vegetable.display_name} ({hours_elapsed:.1f}時間経過)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f'24時間リマインド送信失敗: {vegetable.display_name}'
                        )
                    )
        
        if sent_count == 0:
            self.stdout.write(
                self.style.SUCCESS('送信するリマインドはありませんでした')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'合計 {sent_count} 件のリマインドを送信しました')
            )
