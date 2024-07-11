import json
import logging
from datetime import datetime, date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, TemplateView, CreateView, DetailView, UpdateView

from diary.forms import DiaryModelForm, MealModelForm
from diary.models import Diary, Meal, RegularExpressionWord
from .forms import ImageUploadForm
#from .predict import predict_chocolate, load_chocolate_model, predict_kinoko, load_kinoko_model # predict.py から適切な関数とモデルをインポート
from .predict import predict_chocolate, predict_kinoko, predict_kino_take
from .utils import register_event

logger = logging.getLogger(__name__)


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


class PancettaScheduleEventsView(LoginRequiredMixin, TemplateView):
    """カレンダーイベントのスケジュールを作成して表示する"""
    template_name = 'diary/pancetta.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        """POSTメソッドが呼び出された際の処理を行う"""
        date = request.POST.get('date')
        context = self.schedule_events(date)  # 予定のスケジュールを生成する
        return render(request, self.template_name, context)  # 生成したスケジュールをテンプレートに渡してレンダリング

    def schedule_events(self, date):
        """指定された日付をもとにイベントのスケジュールを生成する"""
        date = datetime.strptime(date, '%Y-%m-%d')  # 入力された日付をdatetimeオブジェクトに変換

        context = {
            'days': [1, 2],  # スケジュールを生成する日数のリスト
            'events': [],  # 生成されたイベントのリスト
        }

        for days in context['days']:
            new_date = date + timedelta(days=days)  # 指定された日数だけ日付を進める
            event_id = register_event(new_date)  # 新しい日付のイベントを登録
            if event_id is not None:
                event = {
                    'days': days,
                    'event_date': new_date.strftime('%Y-%m-%d'),  # 日付を指定の形式で文字列に変換
                    'event_registered': True,  # イベントが登録されたフラグ
                }
            else:
                event = {
                    'days': days,
                    'event_date': new_date.strftime('%Y-%m-%d'),
                    'event_registered': False,  # イベントが登録されなかったフラグ
                }
            context['events'].append(event)  # 生成されたイベントをリストに追加

        return context  # 生成されたスケジュールのコンテキストを返す


class InputCommentView(LoginRequiredMixin, TemplateView):
    template_name = 'diary/input_comment.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def post(self, request, *args, **kwargs):
        comment = request.POST.get('comment')
        context = {'comment': comment}
        return render(request, self.template_name, context)


class MassageView(TemplateView):
    template_name = 'diary/message.html'


class RegularExpressionView(TemplateView):
    template_name = 'diary/regular_expression.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        words = RegularExpressionWord.objects.all()
        context['words'] = words
        return context


# class BiscuitView(View):
#     form_class = ImageUploadForm
#     template_name = 'diary/biscuit.html'
#
#     def get(self, request, *args, **kwargs):
#         form = self.form_class()
#         return render(request, self.template_name, {'form': form})
#
#     def post(self, request, *args, **kwargs):
#         # JSONデータを読み込む
#         data = json.loads(request.body)
#         image_data = data.get('image')
#         if image_data:
#             # 画像データを処理して推論を行う
#             prediction = predict(model, image_data)  # ここで適切に画像データを処理する必要がある
#             return JsonResponse({'prediction': prediction})
#         else:
#             return JsonResponse({'error': 'No image data received'}, status=400)





class BiscuitView(TemplateView):
    template_name = 'diary/biscuit.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        image_data = data.get('image')
        if image_data:
            prediction = predict_chocolate(image_data)
            return JsonResponse({'prediction': prediction})
        else:
            return JsonResponse({'error': 'No image data received'}, status=400)

# class KinokoView(TemplateView):
#     template_name = 'diary/kinoko.html'
#
#     def post(self, request, *args, **kwargs):
#         data = json.loads(request.body)
#         image_data = data.get('image')
#         if image_data:
#             prediction = predict_kinoko(image_data)
#             return JsonResponse({'prediction': prediction})
#         else:
#             return JsonResponse({'error': 'No image data received'}, status=400)

class KinokoView(TemplateView):
    template_name = 'diary/kinoko.html'

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        image_data = data.get('image')
        action = data.get('action')  # アクションを取得
        if image_data:
            if action == 'degree':
                prediction = predict_kino_take(image_data)  # モデルを引数として渡す
                return JsonResponse(prediction)
            else:
                prediction = predict_kinoko(image_data)
                return JsonResponse({'prediction': prediction})
        else:
            return JsonResponse({'error': 'No image data received'}, status=400)