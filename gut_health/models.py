from django.db import models


class DailyCheck(models.Model):
    """日々のチェック記録を保存するモデル"""
    date = models.DateField(unique=True)
    data = models.TextField(default='{}')  # JSON形式でデータを保存
    mood = models.IntegerField(null=True, blank=True)  # 気分/調子: 1-5の評価
    memo = models.TextField(blank=True, default='')  # メモ欄
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        mood_str = f" 調子: {self.mood}/5" if self.mood else ""
        return f"チェック: {self.date}{mood_str}"