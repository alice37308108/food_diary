from django.db import models
from django.utils import timezone
import random


class PickledVegetable(models.Model):
    """ぬか漬け野菜モデル"""
    
    VEGETABLE_CHOICES = [
        ('cucumber', 'きゅうり🥒'),
        ('eggplant', 'なす🍆'),
        ('carrot', 'にんじん🥕'),
        ('cabbage', 'キャベツ🥬'),
        ('pepper', 'ピーマン🌶️'),
        ('tomato', 'トマト🍅'),
        ('radish', 'だいこん🌶️'),
        ('turnip', 'かぶ🌰'),
        ('other', 'その他🥗'),
    ]
    
    vegetable_type = models.CharField(
        max_length=20,
        choices=VEGETABLE_CHOICES,
        verbose_name='野菜の種類'
    )
    custom_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='カスタム名'
    )
    pickled_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='漬けた日時'
    )
    removed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='取り出した日時'
    )
    reminder_24h_sent = models.BooleanField(
        default=False,
        verbose_name='24時間リマインド送信済み'
    )
    reminder_48h_sent = models.BooleanField(
        default=False,
        verbose_name='48時間リマインド送信済み'
    )
    reminder_72h_sent = models.BooleanField(
        default=False,
        verbose_name='72時間リマインド送信済み'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'ぬか漬け野菜'
        verbose_name_plural = 'ぬか漬け野菜'
        ordering = ['-pickled_at']
    
    def __str__(self):
        name = self.custom_name if self.custom_name else self.get_vegetable_type_display()
        return f"{name} ({self.pickled_at.strftime('%m/%d %H:%M')})"
    
    @property
    def is_pickled(self):
        """現在漬けているかどうか"""
        return self.removed_at is None
    
    @property
    def hours_pickled(self):
        """漬けてからの経過時間（時間）"""
        if self.removed_at:
            end_time = self.removed_at
        else:
            end_time = timezone.now()
        
        delta = end_time - self.pickled_at
        return delta.total_seconds() / 3600
    
    @property
    def vegetable_emoji(self):
        """野菜の絵文字を取得"""
        emoji_map = {
            'cucumber': '🥒',
            'eggplant': '🍆',
            'carrot': '🥕',
            'cabbage': '🥬',
            'pepper': '🌶️',
            'tomato': '🍅',
            'radish': '🌶️',
            'turnip': '🌰',
            'other': '🥗',
        }
        return emoji_map.get(self.vegetable_type, '🥗')
    
    @property
    def display_name(self):
        """表示名を取得"""
        if self.custom_name:
            return f"{self.vegetable_emoji}{self.custom_name}"
        return self.get_vegetable_type_display()
    
    def get_reminder_message(self, hours_elapsed):
        """リマインドメッセージを取得"""
        if hours_elapsed >= 72:
            return self._get_72h_message()
        elif hours_elapsed >= 48:
            return self._get_48h_message()
        elif hours_elapsed >= 24:
            return self._get_24h_message()
        return None
    
    def _get_24h_message(self):
        """24時間後メッセージ（5パターンからランダム選択）"""
        messages = [
            f"{self.vegetable_emoji}「もう24時間も温泉に浸かってるから、そろそろ上がりたいんだけど...お迎えお願いします！」",
            f"{self.vegetable_emoji}「24時間もお風呂に入ってたら、指がふやけちゃった！のぼせる前に出してくださーい！」",
            f"{self.vegetable_emoji}「ぬか床ホテルに24時間滞在中です。チェックアウトの時間ですが、お迎えはまだでしょうか？」",
            f"{self.vegetable_emoji}「ぬか床学校で24時間特訓しました！もう卒業できるレベルです。お迎えお待ちしてます！」",
            f"{self.vegetable_emoji}「ぬか床エステで24時間美容パック中でした！もう十分キレイになったので、お迎えお願いします💅」",
        ]
        return random.choice(messages)
    
    def _get_48h_message(self):
        """48時間後メッセージ（5パターンからランダム選択）"""
        messages = [
            "🚨「緊急事態！野菜レスキュー隊出動要請！48時間経過により、私たちはもはや『漬物』を超えて『考古学的発見物』になりかけています！」",
            "🆘「SOS！SOS！48時間漂流中！もはや無人島ならぬ『無人ぬか床』状態です！救助をお願いします！」",
            "🏥「患者：野菜、症状：漬かりすぎ、経過時間：48時間。至急、外科手術（取り出し）が必要です！」",
            "🚀「地球から48時間、ぬか床星に不時着中！地球への帰還ミッション開始をお願いします！」",
            "🔍「事件発生！野菜行方不明事件から48時間経過。最後に目撃されたのはぬか床付近。至急捜索願います！」",
        ]
        return random.choice(messages)
    
    def _get_72h_message(self):
        """72時間後メッセージ（5パターンからランダム選択）"""
        messages = [
            "💀「...私たちのことは忘れて、新しい野菜と幸せになってください...（成仏）」",
            "🦕「72時間経過...私たち、もう化石になっちゃったかも。考古学者の発見を待ちます...」",
            "⚰️「伝説となった野菜たちより...後世に語り継がれる『ぬか床の奇跡』をありがとう...」",
            "👻「うらめしや〜...72時間放置された野菜の怨念です...夜中にぬか床をガタガタ揺らしちゃうぞ〜」",
            "📦「タイムカプセルとして72時間保存されました。未来の人類への贈り物として大切に保管中...」",
        ]
        return random.choice(messages)