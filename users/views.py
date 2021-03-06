from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import hashlib
from .forms import UserRegister, verification
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from posts.models import Profile
import os
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from django.contrib.auth import authenticate, login, logout
def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        ver = verification(request.POST)
        if form.is_valid() and ver.is_valid():
            form.username = request.POST.get('username')
            form.password1 = request.POST.get('password1')
            form.password2 = request.POST.get('password2')
            form.save()
            try:
                new_user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'],)
                login(request, new_user)
            except:
                messages.warning(request, f'there is an error')
                return render(request, 'users/register.html', {"form": form, "ver": ver,})
            profile = request.user.profile
            profile.privatekey = request.POST.get('privatekey')
            profile.publickey = request.POST.get('publickey')
            profile.save()
            return redirect('home')
        else:
            messages.warning(request, "wrong Captcha")
    else:
       form = UserRegister()
       ver = verification()
    return render(request, 'users/register.html', {"form": form, 'ver': ver,})
class Login(View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        return render(request, 'users/login.html', {'ver': ver,})
class Logintwo(View):
    def get(self, request, *args, **kwargs):
        global msg, code
        ver = verification()
        username = request.GET.get('username')
        users = User.objects.filter(username=username)
        if users.exists():
            user = User.objects.get(username=username)
            fa = False
            if user.profile.public_key != '' and user.profile.fingerprint != '' and user.profile.factor_auth == True:
                fa = True
                code = random.randrange(100000, 1545599500051500, 3424)
                msg = os.popen(f'echo "your code is: {code}" | gpg --encrypt --armor --recipient "{user.profile.fingerprint}"').read()
                context = {
                'msg': msg,
                '2fa': fa,
                'ver': ver,
                }
            else:
                fa = False
                context = {
                '2fa': fa,
                'ver': ver,
                }
        else:
            messages.warning(request, 'User Doesn\'t Exist')
            return redirect('login')
        return render(request, 'users/login_two.html', context)
    def post(self, request, *args, **kwargs):
        ver = verification(request.POST)
        username = request.GET.get('username')
        user = User.objects.get(username=username)
        users = User.objects.filter(username=username)
        if users.exists():
            usernames = request.GET.get('username')
            passwords = request.POST.get('password')
            fa = False
            if user.profile.public_key != '' and user.profile.fingerprint != '' and user.profile.factor_auth == True:
                fa = True
            if fa:
                twofa = request.POST.get('2facode')
                if int(twofa) == code:
                    login_user = authenticate(username=usernames,password=passwords,)
                    if login_user and ver.is_valid():
                        login(request, login_user)
                        messages.success(request, 'Logged In Successfully')
                        response = redirect('home')
                        return response
                    else:
                        messages.warning(request, 'Incorrect Data')
                else:
                    messages.warning(request, 'Incorrect Data')
                    return redirect('login')
                context = {
                    '2fa': fa,
                    'msg': msg,
                    'ver': ver,
                }
            else:
                login_user = authenticate(username=username,password=passwords,)
                if login_user and ver.is_valid():
                    login(request, login_user)
                    messages.success(request, 'Logged In Successfully')
                    response = redirect('home')
                    return response
                else:
                    messages.warning(request, 'Incorrect Data')
                context = {
                    '2fa': fa,
                    'ver': ver,
                }
        else:
            messages.warning(request, 'user doesn\'t exist')
            return redirect('login')
        return render(request, 'users/login_two.html', context)
class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('home')
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'logged out successfully')
    return redirect('login')
