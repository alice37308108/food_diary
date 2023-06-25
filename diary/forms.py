from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.utils import timezone

from diary.models import Diary, Meal


class DiaryModelForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['date', 'morning_walking', 'hours_of_sleep', 'sleep_quality', 'weight', 'memo']


class MealModelForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['date', 'meal_type', 'bean', 'sesame', 'seaweed', 'vegetable', 'fish', 'mushroom', 'potato',
                  'fresh_vegetable', 'fermented_food', 'supplement', 'memo', 'photo']
