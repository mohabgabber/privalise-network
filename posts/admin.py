from django.contrib import admin
from .models import Post, Profile, Comment, Tag, Notification, Notes, Message
admin.site.register(Post)
admin.site.register(Message)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Tag)
admin.site.register(Notes)
