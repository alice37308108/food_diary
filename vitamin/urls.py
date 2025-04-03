from django.urls import path
from . import views

app_name = 'vitamin'

urlpatterns = [
    path('', views.home, name='home'),
    path('history/', views.history, name='history'),
]