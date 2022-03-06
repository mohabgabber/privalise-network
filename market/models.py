from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class Product(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.CharField(max_length=150, null=False, blank=False)
    description = models.TextField(blank=False, null=False)
    price = models.FloatField(blank=False, null=False)
    picture = models.ImageField(blank=True, null=True, upload_to='products_images')

class Seller(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    name = models.ForeignKey(User, blank=False, null=False, related_name="sell", on_delete=models.CASCADE)
    
