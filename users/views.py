from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegister
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views import View
from django.contrib.auth.views import PasswordChangeView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
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
        password = request.POST.get('password')
        users = User.objects.filter(username=username)
        if users.exists():
            user = authenticate(username=username,password=password,)
        try:
            login(request, user)
            return redirect("home")
        except:
            messages.success(request, "Incorrect Data")
        return render(request, 'users/login.html')    

class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('home')
@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'logged out successfully')
    return redirect('login')
