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
    path('mago/', views.MagoDiaryView.as_view(), name='mago'),
    path('success/', views.SuccessView.as_view(), name='success'),

    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginFormView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', views.LogoutFormView.as_view(), name='logout'),

]
