from django.contrib import admin
from .models import Post, Profile, Comment, Tag, Notification, Notes, Message, Keys, Chats
admin.site.register(Post)
admin.site.register(Chats)
admin.site.register(Keys)
admin.site.register(Message)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Tag)
admin.site.register(Notes)
