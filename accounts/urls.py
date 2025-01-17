# accounts/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, logout_request

urlpatterns = [
    path('register/', register_view, name='register'),

    # Встроенные вьюхи:
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_request, name='logout'),
]
