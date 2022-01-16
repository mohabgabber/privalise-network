from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import UserRegister
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordChangeView, PasswordResetDoneView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import ContactView
#from django.http import JsonResponse
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

class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('home')

def contact(request):
    if request.method == 'GET':
        form = ContactView()
    else:
        form = ContactView(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            subject = form.cleaned_data['subject']
            from_email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            try:
                send_mail(name, subject, message, from_email, ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('success')
    return render(request, "users/contact.html", {'form': form})

def successView(request):
    return render(request, "contact_success.html")

def logout_view(request):
    logout(request)
    return redirect('two_factor:login')
