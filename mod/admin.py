from django.contrib import admin
from .models import reports, Txs, Wallet
admin.site.register(Txs)
admin.site.register(reports)
admin.site.register(Wallet)