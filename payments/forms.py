from django import forms
from django.forms.widgets import Widget
from django.contrib.auth.models import User
class ReportsForm(forms.ModelForm):
    class Meta:
        model = reports
        fields = ['to_user', 'reason']