from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from accounts.forms import SignupForm, LoginForm, UserUpdateForm


class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'accounts/signup.html'
    success_url = 'diary/index.html'

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('diary:top')


class LoginFormView(LoginView):
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def form_valid(self, form):
        login(self.request, form.get_user())
        next_url = self.request.GET.get('next')
        if next_url:
            return redirect(next_url)
        return super().form_valid(form)


class LogoutFormView(LogoutView):
    template_name = 'diary/index.html'


class UserUpdateView(UpdateView):
    model = User
    template_name = 'accounts/update.html'
    form_class = UserUpdateForm
    success_url = reverse_lazy('diary:index')

    def get_object(self, queryset=None):
        return self.request.user
