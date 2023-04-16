from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from diary.models import Diary


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

