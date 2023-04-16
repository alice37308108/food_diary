from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from diary.models import Diary, Meal


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class LoginForm(AuthenticationForm):
    pass


class DiaryModelForm(forms.ModelForm):
    class Meta:
        model = Diary
        fields = ['date', 'hours_of_sleep', 'sleep_quality', 'weight', 'memo']


class MealModelForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['meal_type', 'bean', 'sesame', 'seaweed', 'vegetable', 'fish', 'mushroom', 'potato',
                  'fresh_vegetable', 'fermented_food', 'supplement', 'memo']
