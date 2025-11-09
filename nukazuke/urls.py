from django.urls import path
from . import views

app_name = 'nukazuke'

urlpatterns = [
    path('', views.index, name='index'),
    path('pickle/', views.pickle_vegetable, name='pickle_vegetable'),
    path('remove/<int:vegetable_id>/', views.remove_vegetable, name='remove_vegetable'),
    path('history/', views.history, name='history'),
    path('test-line/', views.test_line_message, name='test_line_message'),
]
