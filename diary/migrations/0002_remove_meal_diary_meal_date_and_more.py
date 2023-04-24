# Generated by Django 4.2 on 2023-04-20 22:35

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('diary', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meal',
            name='diary',
        ),
        migrations.AddField(
            model_name='meal',
            name='date',
            field=models.DateField(default=datetime.date.today, verbose_name='日付'),
        ),
        migrations.AlterField(
            model_name='diary',
            name='hours_of_sleep',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(24)], verbose_name='睡眠時間'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='bean',
            field=models.BooleanField(verbose_name='ま・まめ\U0001fad8'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='fermented_food',
            field=models.BooleanField(verbose_name='発酵・発酵食品🫕'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='fish',
            field=models.BooleanField(verbose_name='さ・さかな🐟'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='fresh_vegetable',
            field=models.BooleanField(verbose_name='生野菜・発酵食品🥗'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='meal_type',
            field=models.CharField(choices=[('朝ごはん', '朝ごはん'), ('昼ごはん', '昼ごはん'), ('夜ごはん', '夜ごはん'), ('おやつ', 'おやつ')], max_length=4, verbose_name='ごはん'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='memo',
            field=models.TextField(blank=True, verbose_name='メモ'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='mushroom',
            field=models.BooleanField(verbose_name='し・きのこ🍄'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='meal_photos/', verbose_name='写真'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='potato',
            field=models.BooleanField(verbose_name='い・いも🍠'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='seaweed',
            field=models.BooleanField(verbose_name='わ・海藻🏝️'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='sesame',
            field=models.BooleanField(verbose_name='ご・ごま🥜'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='supplement',
            field=models.ManyToManyField(blank=True, to='diary.supplement', verbose_name='サプリメント'),
        ),
        migrations.AlterField(
            model_name='meal',
            name='vegetable',
            field=models.BooleanField(verbose_name='や・野菜🥦'),
        ),
    ]