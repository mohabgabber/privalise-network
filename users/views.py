from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegister
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
import os
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from django.contrib.auth import authenticate, login, logout
def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            form.username = request.POST.get('username')
            form.password1 = request.POST.get('password1')
            form.password2 = request.POST.get('password2')
            try:
                form.save()
            except:
                messages.success(request, f'there is an error')
                return render(request, 'users/register.html', {"form": form})
            username = form.cleaned_data.get('username')
            messages.success(request, f'account created for {username}')
            new_user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'],)
            login(request, new_user)
            return redirect('home')
    else:
       form = UserRegister()
    return render(request, 'users/register.html', {"form": form})  
class Login(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'users/login.html')
    def post(self, request, *args, **kwargs):
        username = request.POST.get('username')
        #password = request.POST.get('password')
        users = User.objects.filter(username=username)
        if users.exists():
            return redirect('login-two', username=username)
        else:
            messages.success(request, "Incorrect Data")
        return render(request, 'users/login.html')    
class Logintwo(View):
    def get(self, request, *args, **kwargs):
        global msg, code
        username = request.GET.get('username')
        users = User.objects.filter(username=username)
        if users.exists():
            user = User.objects.get(username=username)
            fa = False
            if user.profile.public_key != '' and user.profile.fingerprint != '':
                fa = True
                code = random.randrange(100, 100051500, 3424)
                msg = os.popen(f'echo "your code is: {code}" | gpg --encrypt --armor --recipient "{user.profile.fingerprint}"').read()
                context = {
                'msg': msg,
                '2fa': fa,
                }
            else:
                fa = False
                context = {
                '2fa': fa,
                }
        else:
            messages.success(request, 'User Doesn\'t Exist')
            return redirect('login')
        return render(request, 'users/login_two.html', context)
    def post(self, request, *args, **kwargs):
        username = request.GET.get('username')
        user = User.objects.get(username=username)
        users = User.objects.filter(username=username)
        if users.exists():
            usernames = request.GET.get('username')
            passwords = request.POST.get('password')
            fa = False
            if user.profile.public_key != '' and user.profile.fingerprint != '':
                fa = True
            if fa: 
                twofa = request.POST.get('2facode')
                if int(twofa) == code:
                    login_user = authenticate(username=usernames,password=passwords,)
                    if login_user:
                        login(request, login_user)
                        return redirect('home')
                    else:
                        messages.success(request, 'Incorrect Data')
                else:
                    messages.success(request, 'Incorrect Data')
                    return redirect('login')
                context = {
                    '2fa': fa,
                    'msg': msg,
                }
            else:
                login_user = authenticate(username=username,password=passwords,)
                if login_user:
                    login(request, login_user)
                    return redirect('home')
                else:
                    messages.success(request, 'Incorrect Data')
                context = {
                    '2fa': fa,
                }
        else:
            messages.success(request, 'user doesn\'t exist')
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
