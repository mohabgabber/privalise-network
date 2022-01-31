from django import forms
from django.forms.widgets import Widget
from django.contrib.auth.models import User
from .models import reports
class ReportsForm(forms.ModelForm):
    class Meta:
        model = reports
        fields = ['reason']