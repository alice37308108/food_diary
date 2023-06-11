from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    # path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginFormView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', views.LogoutFormView.as_view(), name='logout'),
    # path('update/', views.UserUpdateView.as_view(), name='update'),
]
