from django.urls import path

from . import views

urlpatterns = [

    path('login', views.LoginUser.as_view(), name='api_login'),
    path('register', views.RegisterUser.as_view(), name='api_register'),
]