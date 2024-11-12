from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="カテゴリー名")

    def __str__(self):
        return self.name

class GratitudePhrase(models.Model):
    text = models.TextField(verbose_name="感謝のフレーズ")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="ジャンル")

    def __str__(self):
        return f"{self.category} - {self.text[:20]}"
