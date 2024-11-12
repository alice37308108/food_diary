from django.urls import reverse_lazy
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
