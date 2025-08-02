from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    """心地よさのカテゴリ"""
    CATEGORY_CHOICES = [
        ('heart', '🌱 心'),
        ('body', '🍔 からだ'),
        ('space', '🏠 空間'),
        ('time', '⏰ 時間'),
        ('mind', '💡 思考'),
        ('relationship', '🧸 人間関係'),
        ('hobby', '🌻 好きなこと'),
        ('self', '💝 自分'),
    ]
    
    name = models.CharField(max_length=20, choices=CATEGORY_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    emoji = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.emoji} {self.display_name}"

class ComfortAction(models.Model):
    """心地よさアクション"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category, verbose_name="カテゴリ")
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    estimated_minutes = models.PositiveIntegerField(default=5)  # 所要時間（分）
    is_favorite = models.BooleanField(default=False)  # お気に入り
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        category_names = ", ".join([cat.display_name for cat in self.categories.all()])
        return f"{self.name} ({category_names})"
    
    def execution_count(self):
        """実行回数を取得"""
        return self.actionexecution_set.count()
    
    def average_comfort_level(self):
        """平均すっきり度を取得"""
        executions = self.actionexecution_set.all()
        if not executions:
            return 0
        return sum(ex.comfort_level for ex in executions) / len(executions)

class ActionExecution(models.Model):
    """アクション実行記録"""
    action = models.ForeignKey(ComfortAction, on_delete=models.CASCADE)
    executed_at = models.DateTimeField(default=timezone.now)
    comfort_level = models.PositiveIntegerField(
        choices=[(i, f"★{'★' * (i-1)}{'☆' * (5-i)}") for i in range(1, 6)],
        default=3
    )  # 1-5のすっきり度
    memo = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.action.name} - {self.executed_at.strftime('%Y-%m-%d %H:%M')}"

class HappinessRecord(models.Model):
    """小さな幸せ記録"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    photo = models.ImageField(upload_to='happiness_photos/', blank=True, null=True)
    recorded_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.title} - {self.recorded_at.strftime('%Y-%m-%d')}"
