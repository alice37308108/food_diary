import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Diary(models.Model):
    date = models.DateField(verbose_name='日付', unique=True)
    hours_of_sleep = models.IntegerField(verbose_name='睡眠時間',
                                         validators=[MinValueValidator(1), MaxValueValidator(24)])
    sleep_quality = models.IntegerField(verbose_name='睡眠の質', validators=[MinValueValidator(1), MaxValueValidator(5)])
    weight = models.FloatField(verbose_name='体重', blank=True, null=True)
    memo = models.CharField(max_length=200, blank=True, verbose_name='メモ')

    def __str__(self):  # これを書かないとadminやフォームで画面でDiary object (1)と表示される
        return self.date.strftime('%Y/%m/%d')

    def get_absolute_url(self):
        return reverse('diary:list')


class Meal(models.Model):
    date = models.ForeignKey(Diary, on_delete=models.CASCADE, verbose_name='日付', to_field='date')
    DATE_CHOICES = (
        ('朝ごはん', '朝ごはん'),
        ('昼ごはん', '昼ごはん'),
        ('夜ごはん', '夜ごはん'),
        ('おやつ', 'おやつ'),
    )
    meal_type = models.CharField(max_length=4, choices=DATE_CHOICES, verbose_name='ごはん')
    bean = models.BooleanField(verbose_name='ま・まめ🫘')
    sesame = models.BooleanField(verbose_name='ご・ごま🥜')
    seaweed = models.BooleanField(verbose_name='わ・海藻🏝️')
    vegetable = models.BooleanField(verbose_name='や・野菜🥦')
    fish = models.BooleanField(verbose_name='さ・さかな🐟')
    mushroom = models.BooleanField(verbose_name='し・きのこ🍄')
    potato = models.BooleanField(verbose_name='い・いも🍠')
    fresh_vegetable = models.BooleanField(verbose_name='生野菜・発酵食品🥗')
    fermented_food = models.BooleanField(verbose_name='発酵・発酵食品🫕')
    supplement = models.ManyToManyField('Supplement', blank=True, verbose_name='サプリメント')
    memo = models.TextField(blank=True, verbose_name='メモ')
    photo = models.ImageField(upload_to='meal_photos/', blank=True, null=True, verbose_name='写真')
    date = models.DateField(verbose_name='日付', default=datetime.date.today)

    def get_absolute_url(self):
        return reverse('diary:meal_detail', args=[str(self.id)])

    def get_bean(self):
        return '🫘' if self.bean else ''

    def get_sesame(self):
        return '🥜' if self.sesame else ''

    def get_seaweed(self):
        return '🏝️' if self.seaweed else ''

    def get_vegetable(self):
        return '🥦' if self.vegetable else ''

    def get_fish(self):
        return '🐟' if self.fish else ''

    def get_mushroom(self):
        return '🍄' if self.mushroom else ''

    def get_potato(self):
        return '🍠' if self.potato else ''

    def get_fresh_vegetable(self):
        return '🥗' if self.fresh_vegetable else ''

    def get_fermented_food(self):
        return '🫕' if self.fermented_food else ''


class Supplement(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
