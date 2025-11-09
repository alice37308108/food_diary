from django.urls import path
from . import views

app_name = 'nukazuke'

urlpatterns = [
    path('', views.index, name='index'),
    path('pickle/', views.pickle_vegetable, name='pickle_vegetable'),
    path('remove/<int:vegetable_id>/', views.remove_vegetable, name='remove_vegetable'),
    path('history/', views.history, name='history'),
    path('test-line/', views.test_line_message, name='test_line_message'),
    path('manage-vegetables/', views.manage_vegetables, name='manage_vegetables'),
    path('add-vegetable-type/', views.add_vegetable_type, name='add_vegetable_type'),
    path('edit-vegetable-type/<int:vegetable_type_id>/', views.edit_vegetable_type, name='edit_vegetable_type'),
    path('delete-vegetable-type/<int:vegetable_type_id>/', views.delete_vegetable_type, name='delete_vegetable_type'),
    path('delete-history/<int:vegetable_id>/', views.delete_history, name='delete_history'),
    path('delete-all-history/', views.delete_all_history, name='delete_all_history'),
    path('delete-completed-history/', views.delete_completed_history, name='delete_completed_history'),
]
