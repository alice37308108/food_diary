from django.urls import path
from . import views

app_name = 'gut_health'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('export-csv/', views.ExportCSVView.as_view(), name='export_csv'),
    path('export-csv/form/', views.ExportCSVFormView.as_view(), name='export_csv_form'),
]