from django.shortcuts import render
from django.contrib import messages
from django.views import View 
from mod.models import Txs, Wallet
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from posts.validations import valid_addr, valid_sig, create_addr, pay, receive, check_addr, check_conf, check_conf_number, gpgkeyimport
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from users.forms import verification
from .models import *
# PRODUCTS LISTING HANDLING

class products_list(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.all().order_by('-date')
        
        return render(request, "market/list.html", {'products': products,})