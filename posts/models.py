from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
import uuid

class Post(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    image = models.ImageField(blank=True, null=True, upload_to='post_image')
    content = models.TextField()
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    dislikes = models.ManyToManyField(User, blank=True, default=None, related_name='dislikes')
    shared_body  = models.TextField(blank=True, null=True)
    shared_on = models.DateTimeField(blank=True, null=True)
    shared_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='+')
    favourites = models.ManyToManyField(User, related_name='favourite', default=None, blank=True)
    likes = models.ManyToManyField(User, related_name='like', default=None, blank=True)
    tags = models.ManyToManyField('Tag', blank=True)
    mentions = models.ManyToManyField(User, related_name='mentions', blank=True)
    def create_tags(self):
        for word in self.content.split():
            if (word[0] == '$'):
                tag = Tag.objects.filter(name=word[1:]).first()
                if tag:
                    self.tags.add(tag.pk)
                else:
                    tag = Tag(name=word[1:])
                    tag.save()
                    self.tags.add(tag.pk)
                self.save()
        if self.shared_body:
            for word in self.shared_body.split():
                if (word[0] == '$'):
                    tag = Tag.objects.filter(name=word[1:]).first()
                    if tag:
                        self.tags.add(tag.pk)
                    else:
                        tag = Tag(name=word[1:])
                        tag.save()
                        self.tags.add(tag.pk)
                    self.save()
    class Meta:
        ordering = ['-date_posted']#, '-shared_on']
    def __str__(self):
        return self.content
    def get_absolute_url(self):
        return reverse("post-detail", kwargs={"id": self.id})

class Comment(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name='author')
    date_created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')
    parent = models.ForeignKey('self', blank=True, on_delete=models.CASCADE, null=True, related_name='+')
    likescount = models.IntegerField(default=0)
    def create_tags(self):
        for word in self.content.split():
            if (word[0] == '$'):
                tag = Tag.objects.get(name=word[1:])
                if tag:
                    self.tags.add(tag.pk)
                else:
                    tag = Tag(name=word[1:])
                    tag.save()
                    self.tags.add(tag.pk)
                self.save()
    class Meta:
        ordering = ['-date_created']
    def __str__(self):
        return '{} by {}'.format(self.content, self.author)
    @property
    def children(self):
        return Comment.objects.filter(parent=self).order_by("date_created").all()
    @property
    def is_parent(self):
        if self.parent is None:
            return True
        return False

class Profile(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=250, blank=True, default='')
    public_key = models.TextField(blank=True, default='')
    name = models.CharField(max_length=30, blank=True, default='')
    xmppusername = models.CharField(max_length=20, blank=True, default='')
    xmppserver = models.CharField(max_length=62, blank=True, default='')
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    verified = models.BooleanField(default=False)
    followers_count = models.BigIntegerField(default='0')
    mention_count = models.BigIntegerField(default='0')
    factor_auth = models.BooleanField(default=False)
    fingerprint = models.CharField(max_length=100, blank=True)
    privatekey = models.TextField()
    publickey = models.TextField()
    def __str__(self):
        return f'{self.user.username} Profile'


class Keys(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    partner1 = models.ForeignKey(User, related_name='partner1', on_delete=models.CASCADE)
    partner2 = models.ForeignKey(User, related_name='partner2', on_delete=models.CASCADE)
    shared_key1 = models.TextField()
    shared_key2 = models.TextField()

class Chats(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    partners = models.ManyToManyField(User, blank=True, related_name='partners')

class Message(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    msg = models.TextField(null=False, blank=False)
    date = models.DateTimeField(default=timezone.now)
    to = models.ForeignKey(User, related_name='received', on_delete=models.CASCADE, blank=False, null=False)
    author = models.ForeignKey(User, blank=False, null=False, related_name='sent', on_delete=models.CASCADE)

class Tag(models.Model):
    name = models.CharField(max_length=255)

class About(models.Model):
    content = models.TextField()

class Notification(models.Model):
    # 1 = Like, 2 = Comment, 3 = Follow, #4 = Mention
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    user_has_seen = models.BooleanField(default=False)

'''
class Hashtag(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True, unique=True)
    posts = models.ManyToManyField(Post)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title
'''

class Notes(models.Model):
    id = models.UUIDField(primary_key = True, default = uuid.uuid4, editable = False)
    content = models.TextField(blank=False)
    author = models.ForeignKey(User, related_name='notes', blank=False, null=False, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)