from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from posts.models import Post
class Txs(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    rec_addr = models.CharField(max_length=106, blank=False)
    amnt = models.FloatField(blank=False, null=False)
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE, null=False, default='Anonymous')
    confs = models.IntegerField()
    types = models.CharField(max_length=8, blank=False) 
    hash = models.CharField(blank=False, null=False, max_length=64)
    receiver = models.ForeignKey(User, related_name='receiver', on_delete=models.CASCADE, blank=True, null=True)
    message = models.CharField(blank=True, default='Thank You So Much', max_length=50)
    def __str__(self):
        return f'{self.sender} Sent {self.amnt}'

class Wallet(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    balance = models.FloatField(blank=False, null=False, default=0.0)
    user = models.ForeignKey(User, related_name='wallet', on_delete=models.CASCADE, null=False)
    trx = models.ManyToManyField(Txs, related_name='txs', blank=True)
    def __str__(self):
        return f'{self.user.username} Has {self.balance}'

class reports(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    from_user = models.ForeignKey(User, related_name='report_from', on_delete=models.CASCADE, null=False) 
    to_user = models.ForeignKey(User, related_name='report_to', on_delete=models.CASCADE, null=False)
    reason = models.TextField(blank=False)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='report_post', blank=False, null=False)
    def __str__(self):
        return f'{self.from_user} Reported {self.to_user}'