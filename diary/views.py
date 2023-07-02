from datetime import datetime, date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, CreateView, DetailView, UpdateView

from diary.forms import DiaryModelForm, MealModelForm
from diary.models import Diary, Meal
from .utils import add_days, register_event


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


class ListDiaryView(LoginRequiredMixin, ListView):
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


class SuccessView(TemplateView):
    template_name = 'diary/success.html'


class PancettaScheduleEventsView(TemplateView):
    template_name = 'diary/pancetta.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        self.schedule_events()
        return redirect('diary:index')

    def schedule_events(self):
        date = '2023-07-01'
        date = datetime.strptime(date, '%Y-%m-%d')

        # for days in [3, 7, 14, 21]:
        for days in [1]:
            new_date = add_days(date, days)
            print(f"{days}日後の日付: {new_date.strftime('%Y-%m-%d')}")

            event_id = register_event(new_date)
            if event_id is not None:
                print(f"{days}日後:{new_date.strftime('%Y-%m-%d')}の予定が登録されました。")
            else:
                print(f"{days}日後の予定の登録に失敗しました。")