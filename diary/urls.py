from django.urls import path
from diary.views import (ListDiaryView,
                         IndexView,
                         SignupView,
                         LoginFormView,
                         LogoutFormView,
                         ItemDetailView,
                         CreateDiaryView)

app_name = 'diary'
urlpatterns = [
    # path('', TemplateView.as_view(template_name='index.html'), name='index'),

    path('', IndexView.as_view(), name='index'),
    path('list/', ListDiaryView.as_view(), name='list'),
    path('detail/<int:pk>/', ItemDetailView.as_view(), name='detail'),
    path('create_diary/', CreateDiaryView.as_view(), name='create_diary'),

    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginFormView.as_view(redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutFormView.as_view(), name='logout'),

]
