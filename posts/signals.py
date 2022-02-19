from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, Notification, Chats
from posts.validations import create_addr
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        monero_address = create_addr()
        Profile.objects.create(user=instance, rec_addr=monero_address[0], name='Anonymous')
        Chats.objects.create(user=instance)
@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

