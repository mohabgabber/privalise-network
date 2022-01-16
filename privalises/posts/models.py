from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
#from PIL import Image
import PIL.Image
import json
class Post(models.Model):
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
    like_count = models.BigIntegerField(default='0')
    tags = models.ManyToManyField('Tag', blank=True)
    mentions = models.ManyToManyField(User, related_name='mentions', blank=True)
    def create_tags(self):
        for word in self.content.split():
            if (word[0] == '#'):
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
                if (word[0] == '#'):
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
        return reverse("post-detail", kwargs={"pk": self.pk})
class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE,related_name='comments')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE,related_name='author')
    date_created = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, blank=True, related_name='comment_likes')
    dislikes = models.ManyToManyField(User, blank=True, related_name='comment_dislikes')
    parent = models.ForeignKey('self', blank=True, on_delete=models.CASCADE, null=True, related_name='+')
    def create_tags(self):
        for word in self.content.split():
            if (word[0] == '#'):
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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True, null=True)
    name = models.CharField(max_length=30, blank=True, null=True)
    followers = models.ManyToManyField(User, blank=True, related_name='followers')
    verified = models.BooleanField(default=False)
    followers_count = models.BigIntegerField(default='0')
    mention_count = models.BigIntegerField(default='0')
    def __str__(self):
        return f'{self.user.username} Profile'
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        img = PIL.Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
class Tag(models.Model):
    name = models.CharField(max_length=255)
class Image(models.Model):
    image = models.ImageField(upload_to='uploads/post_photos', blank=True, null=True)
class Notification(models.Model):
    # 1 = Like, 2 = Comment, 3 = Follow, #4 = Mention
    notification_type = models.IntegerField()
    to_user = models.ForeignKey(User, related_name='notification_to', on_delete=models.CASCADE, null=True)
    from_user = models.ForeignKey(User, related_name='notification_from', on_delete=models.CASCADE, null=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='+', blank=True, null=True)
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
