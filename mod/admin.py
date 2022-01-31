from django.contrib import admin
from .models import reports, txs
admin.site.register(txs)
admin.site.register(reports)