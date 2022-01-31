from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import reports, txs
from django.views import View
from django.http import HttpResponseRedirect
from monero.address import address 
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
#from posts.validations import valid_sig #create_addr, pay, receive, check_addr, check_conf
from users.forms import verification
from posts.models import Post
from django.urls import reverse_lazy
from .forms import ReportsForm
from .models import reports
class ReportPost(LoginRequiredMixin ,View):
    def get(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id) 
        form = ReportsForm()
        ver = verification()
        return render(request, 'mod/report.html', {'form': form, 'post': post, 'ver': ver})
    def post(self, request, id, *args, **kwargs):
        form = ReportsForm(request.POST)
        ver = verification(request.POST)
        post = Post.objects.get(id=id)
        if form.is_valid() and ver.is_valid():
            form.reason = request.POST.get('reason')
            form.from_user = request.user
            form.to_user = post.author
            sign = f'''
{form.reason}
            '''
            if valid_sig(sign, form.id):
                form.save()
                messages.success(request, 'Reported A Mod Will Review Your Request. Thanks!')
            else:
                messages.warning(request, 'Invalid Signature!')
                return redirect('home')
        return render(request, 'mod/report.html', {'form': form, 'post': post, 'ver': ver})