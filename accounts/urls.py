from django.urls import path, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.decorators import login_required
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='jobs:home'), name='logout'),
    path('profile/', login_required(views.ProfileView.as_view()), name='profile'),
    path('settings/', login_required(views.SettingsView.as_view()), name='settings'),
    path('password/change/', 
         login_required(PasswordChangeView.as_view(
             template_name='accounts/change_password.html',
             success_url=reverse_lazy('accounts:password_change_done')
         )), 
         name='change_password'),
    path('password/change/done/', 
         login_required(PasswordChangeDoneView.as_view(
             template_name='accounts/password_change_done.html'
         )), 
         name='password_change_done'),
]
