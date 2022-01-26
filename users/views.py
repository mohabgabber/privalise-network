from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegister
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views.generic.edit import CreateView
def register(request):
    if request.method == 'POST':
        form = UserRegister(request.POST)
        if form.is_valid():
            form.username = request.POST.get('username')
            form.password1 = request.POST.get('password1')
            form.password2 = request.POST.get('password2')
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'account created for {username}')
            new_user = authenticate(username=form.cleaned_data['username'],password=form.cleaned_data['password1'],)
            login(request, new_user)
            return redirect('home')
    else:
       form = UserRegister()
    return render(request, 'users/register.html', {"form": form})
def LoginView(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
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
def logout_view(request):
    logout(request)
    return redirect('login')
