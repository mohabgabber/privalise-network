from django.urls import path
from .views import PasswordChange, LoginView, register, logout_view
urlpatterns = [
    path('register/', register, name='register'),
    path('login/', LoginView, name='login'),
    path('logout/', logout_view, name='logout'),
    path('password-change/', PasswordChange.as_view(), name='password-change'),
]