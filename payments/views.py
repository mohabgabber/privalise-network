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
#from posts.xmrscript import create_addr, pay, receive, check_addr, check_conf
from users.forms import verification
from django.urls import reverse_lazy
from .forms import ReportsForm
