from django.urls import path
from .views import (
    GratitudeCategorySelectView,
    GratitudePhraseListView,
    GratitudePhraseDetailView,
    GratitudePhraseCreateView,
    GratitudePhraseUpdateView,
    GratitudePhraseDeleteView
)

urlpatterns = [
    path('', GratitudeCategorySelectView.as_view(), name='gratitude_category_select'),  # ジャンル選択
    path('list/<str:category>/', GratitudePhraseListView.as_view(), name='gratitude_list'),  # 選択したジャンルのフレーズ一覧
    path('<int:pk>/', GratitudePhraseDetailView.as_view(), name='gratitude_detail'),
    path('add/', GratitudePhraseCreateView.as_view(), name='gratitude_create'),
    path('<int:pk>/edit/', GratitudePhraseUpdateView.as_view(), name='gratitude_update'),
    path('<int:pk>/delete/', GratitudePhraseDeleteView.as_view(), name='gratitude_delete'),
    #path('gratitude/<str:category>/', GratitudePhraseListView.as_view(), name='gratitude_list'),
    #path('gratitude/<category>/', GratitudePhraseListView.as_view(), name='gratitude_list'),
    path('categories/<int:category_id>/', GratitudePhraseListView.as_view(), name='gratitude_list'),
]