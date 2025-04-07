from django.urls import path
from .views import HomeView, HistoryView

app_name = 'vitamin'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('history/', HistoryView.as_view(), name='history'),
]