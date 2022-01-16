from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
class UserRegister(UserCreationForm):
    def clean(self):
        cleaned_data = super(UserRegister, self).clean()
        username = cleaned_data.get('username')
        if username and User.objects.filter(username__iexact=username).exists():
            self.add_error('username', 'A user with that username already exists.')
        return cleaned_data
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
 
class ContactView(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(required=True)
    subject = forms.CharField(required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)