from datetime import datetime, date

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.views.generic import ListView, TemplateView, CreateView, DetailView

from diary.forms import SignupForm, LoginForm
from diary.models import Diary, Meal


class IndexView(TemplateView):
    template_name = 'diary/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = datetime.now().strftime('%Y/%m/%d %H:%M')
        now_hour = datetime.now().hour
        if 5 <= now_hour < 10:
            context['message'] = 'おはようございます'
        elif 10 <= now_hour < 18:
            context['message'] = 'こんにちは'
        else:
            context['message'] = 'こんばんは'
        return context


class ListDiaryView(ListView):
    model = Diary
    template_name = 'diary/list.html'
    paginate_by = 5
    ordering = ['-date'] # 降順


class ItemDetailView(LoginRequiredMixin, DetailView):
    model = Diary
    template_name = 'diary/detail.html'
    context_object_name = 'diary'

    def get_queryset(self):
        return Diary.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CreateDiaryView(LoginRequiredMixin, CreateView):
    model = Diary
    template_name = 'diary/create_diary.html'
    fields = ['date', 'hours_of_sleep', 'sleep_quality', 'weight', 'memo']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = date.today()
        return initial


class CreateMealView(LoginRequiredMixin, CreateView):
    model = Meal
    template_name = 'diary/create_meal.html'
    fields = ['date', 'meal_type', 'bean', 'sesame', 'seaweed', 'vegetable', 'fish', 'mushroom', 'potato',
              'fresh_vegetable', 'fermented_food', 'supplement', 'memo']

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'diary/signup.html'
    success_url = 'diary/index.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('diary:top')


class LoginFormView(LoginView):
    form_class = LoginForm
    template_name = 'diary/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)


class LogoutFormView(LogoutView):
    template_name = 'diary/index.html'
