from django.urls import path
from . import views

app_name = 'comfort_list'

urlpatterns = [
    path('', views.index, name='index'),  # 心地よさリスト一覧
    path('actions/', views.action_list, name='action_list'),  # アクション一覧
    path('actions/add/', views.add_action, name='add_action'),  # アクション追加
    path('actions/<int:action_id>/execute/', views.execute_action, name='execute_action'),  # アクション実行
    path('happiness/', views.happiness_list, name='happiness_list'),  # 小さな幸せ一覧
    path('happiness/add/', views.add_happiness, name='add_happiness'),  # 小さな幸せ追加
    path('category/<str:category_name>/', views.category_actions, name='category_actions'),  # カテゴリ別アクション
] 