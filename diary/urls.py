from django.urls import path
from . import views

app_name = 'diary'
urlpatterns = [
    path('', views.IndexView.as_view(), name='redirect'),

    path('index/', views.IndexView.as_view(), name='index'),
    path('list/', views.ListDiaryView.as_view(), name='list'),
    path('detail/<int:pk>/', views.ItemDetailView.as_view(), name='detail'),
    path('create_diary/', views.CreateDiaryView.as_view(), name='create_diary'),
    path('create_meal/', views.CreateMealView.as_view(), name='create_meal'),
    path('update_diary/<int:pk>/', views.UpdateDiaryView.as_view(), name='update_diary'),
    path('update_meal/<int:pk>/', views.UpdateMealView.as_view(), name='update_meal'),
    path('mago/', views.MagoDiaryView.as_view(), name='mago'),
    path('success/', views.SuccessView.as_view(), name='success'),
    path('pancetta/', views.PancettaScheduleEventsView.as_view(), name='pancetta'),
    path('input_comment/', views.InputCommentView.as_view(), name='input_comment'),
    path('message/', views.MassageView.as_view(), name='message'),
    path('regular_expression/', views.RegularExpressionView.as_view(), name='regular_expression'),
]
