from datetime import datetime, date

from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, DetailView, UpdateView

from diary.forms import SignupForm, LoginForm, DiaryModelForm, MealModelForm
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
    ordering = ['-date']  # 降順


class MagoDiaryView(TemplateView):
    template_name = 'diary/mago.html'


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
    template_name = 'diary/create_diary.html'
    form_class = DiaryModelForm
    success_url = reverse_lazy('diary:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_initial(self):
        initial = super().get_initial()
        initial['date'] = date.today()
        return initial


class UpdateDiaryView(LoginRequiredMixin, UpdateView):
    template_name = 'diary/create_diary.html'
    model = Diary
    form_class = DiaryModelForm
    success_url = reverse_lazy('diary:list')

    def get_queryset(self):
        return Diary.objects.all()

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class CreateMealView(LoginRequiredMixin, CreateView):
    template_name = 'diary/create_meal.html'
    form_class = MealModelForm
    success_url = reverse_lazy('diary:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class UpdateMealView(LoginRequiredMixin, UpdateView):
    template_name = 'diary/create_meal.html'
    model = Meal
    form_class = MealModelForm
    success_url = reverse_lazy('diary:list')

    def get_queryset(self):
        return Meal.objects.all()

    def get_object(self, queryset=None):
        try:
            obj = super().get_object(queryset=queryset)
        except Http404:
            raise Http404("データがありません")
        if obj.user != self.request.user:
            raise Http404("データがありません")
        return obj

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


class SuccessView(TemplateView):
    template_name = 'diary/success.html'


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
