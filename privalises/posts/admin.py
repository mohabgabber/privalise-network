from django.contrib import admin
from .models import Post, Profile, Comment, Tag, Notification
admin.site.register(Post)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Tag)
