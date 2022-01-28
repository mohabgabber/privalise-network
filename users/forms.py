from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from captcha.fields import CaptchaField

class UserRegister(UserCreationForm):
    def clean(self):
        cleaned_data = super(UserRegister, self).clean()
        username = cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            self.add_error('username', 'A user with that username already exists.')
        return cleaned_data
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
class verification(forms.Form):
    captcha=CaptchaField()
