from django.urls import path
from . import views
#from django.conf import settings
#from django.conf.urls.static import static
from django.contrib.auth import views as auth_views 
from django.conf import settings
from .views import PasswordChange#, validate_username, PasswordDone
urlpatterns = [
    path('register/', views.register, name='register'),
    path('contact/', views.contact, name='contact'),
    # path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
    path('password-change/', PasswordChange.as_view(), name='password-change'),
    #path('validate_username', validate_username, name='validate_username')
    #path('password-change/done/', PasswordDone.as_view(), name='password-change-done')
]
#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)