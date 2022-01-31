from django.urls import path
from .views import ReportPost 
urlpatterns = [
    path('report/post/<str:id>', ReportPost.as_view(), name='report-post'),
]