import random

from django import forms
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .models import GratitudePhrase, Category


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


# ジャンル選択とおすすめ表示のビュー
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
