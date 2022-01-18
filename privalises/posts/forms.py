from django import forms
from django.forms.widgets import Widget
from .models import Profile, Comment, Post
from django.contrib.auth.models import User
#class ShareForm(forms.form):
#    body = forms.CharField(label='', widget=forms.Textarea(attrs={
#         'rows': '3',
#         'placeholder': 'say something..'
#        }))
class ProfileUpdteForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'bio', 'public_key', 'image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['content']
