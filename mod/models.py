from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import uuid
from posts.models import Post
class Txs(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    rec_addr = models.CharField(max_length=106, blank=False)
    amnt = models.FloatField()
    sender = models.ForeignKey(User, related_name='sender', on_delete=models.CASCADE, null=False)
    def __str__(self):
        return f'{self.sender} Sent {self.amnt}'
class reports(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    from_user = models.ForeignKey(User, related_name='report_from', on_delete=models.CASCADE, null=False) 
    to_user = models.ForeignKey(User, related_name='report_to', on_delete=models.CASCADE, null=False)
    reason = models.TextField(blank=False)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='report_post', blank=False, null=False)
    def __str__(self):
        return f'{self.from_user} Reported {self.to_user}'