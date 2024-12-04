import json
import os
import random

import requests
from django import forms
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.views.generic.edit import FormView
from dotenv import load_dotenv

from .models import Category
from .models import GratitudePhrase

# from .forms import CategorySelectForm

# .envファイルを読み込む
load_dotenv()


# ジャンル選択のビュー
class GratitudeCategorySelectView(ListView):
    model = Category
    template_name = "gratitude/gratitude_category_select.html"
    context_object_name = "categories"


# 選んだジャンルのフレーズ一覧を表示するビュー
class GratitudePhraseListView(ListView):
    model = GratitudePhrase
    template_name = 'gratitude/gratitude_list.html'  # 使用するテンプレート名
    context_object_name = 'phrases'  # テンプレート内で使う変数名
    paginate_by = 5  # 1ページに表示する件数

    def get_queryset(self):
        # URLからカテゴリーのIDを取得
        category_id = self.kwargs.get('category_id')
        # カテゴリーIDでフィルタリング
        return GratitudePhrase.objects.filter(category_id=category_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # カテゴリーIDをテンプレートに渡す（必要であれば）
        context['category_id'] = self.kwargs.get('category_id')
        return context


class GratitudePhraseDetailView(DetailView):
    model = GratitudePhrase
    template_name = "gratitude/gratitude_detail.html"
    context_object_name = "phrase"


class GratitudePhraseCreateView(CreateView):
    model = GratitudePhrase
    template_name = "gratitude/gratitude_form.html"
    fields = ['text', 'category']
    success_url = reverse_lazy("gratitude_list")


class GratitudePhraseUpdateView(UpdateView):
    model = GratitudePhrase
    template_name = "gratitude/gratitude_form.html"
    fields = ['text', 'category']
    success_url = reverse_lazy("gratitude_list")


class GratitudePhraseDeleteView(DeleteView):
    model = GratitudePhrase
    template_name = "gratitude/gratitude_confirm_delete.html"
    success_url = reverse_lazy("gratitude_list")


# ジャンル選択フォーム
class CategorySelectForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        label="ジャンルを選んでください",
        empty_label="選択してください",
    )


class GratitudeRecommendationView(FormView):
    template_name = "gratitude/recommendation.html"
    form_class = CategorySelectForm

    def form_valid(self, form):
        # フォームから選択されたカテゴリー
        category = form.cleaned_data['category']
        # ランダムでフレーズを選択
        phrases = GratitudePhrase.objects.filter(category=category)
        recommended_phrase = random.choice(phrases) if phrases.exists() else None

        # コンテキストをテンプレートに渡す
        return self.render_to_response(self.get_context_data(
            form=form,
            category=category,
            recommended_phrase=recommended_phrase
        ))

    def form_invalid(self, form):
        # 無効な場合、再度フォームを表示
        return self.render_to_response(self.get_context_data(form=form))

    def post(self, request, *args, **kwargs):
        # 「LINEに送る」ボタンが押された場合
        if 'send_to_line' in request.POST:
            return self.send_line_message(request)  # request を渡す
        else:
            # 通常のフォーム処理を実行
            return super().post(request, *args, **kwargs)

    def send_line_message(self, request):
        access_token = os.getenv("LINE_ACCESS_TOKEN")
        user_id = os.getenv("LINE_USER_ID")

        url = "https://api.line.me/v2/bot/message/push"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        # 画像のURLを静的ファイルとして取得
        #image_url = request.build_absolute_uri(static("gratitude/images/obu_rooting.png"))
        image_url = "https://alice-food-diary.com/static/gratitude/images/obu_rooting.png"

        data = {
            "to": user_id,
            "messages": [
                {
                    "type": "template",
                    # "text": request.POST.get("message", "Default Message")  # テキストメッセージ
                    "altText": "今日のことば💛",
                    "template": {
                        "type": "buttons",
                        "thumbnailImageUrl": image_url,
                        "title": "今日のことば💛",
                        "text": request.POST.get("message", "Default Message"),  # テキストメッセージ
                        "actions": [
                            {
                                "type": "uri",
                                "label": "もっと見る",
                                "uri": "https://alice-food-diary.com"
                            }
                        ]
                    }
                },
            ]
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))

        if response.status_code == 200:
            return JsonResponse({"status": "success", "message": "メッセージが送信されました"})
        else:
            return JsonResponse({
                "status": "error",
                "error_code": response.status_code,
                "error_message": response.text
            })

# テンプレートビューの作成
class MorningAffirmationView(TemplateView):
    template_name = "gratitude/morning_affirmation.html"
