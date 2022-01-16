
from .models import Post
from django.contrib.auth.models import User

from typing import List

'''
def process_post_content(post):
    process_hashtags_from_post_content(post)
    process_mentions_from_post_content(post)

def process_hashtags_from_post_content(post):
    old_hashtags = post.hashtag_set.all()

    if old_hashtags:
        to_delete = get_hashtags_to_delete(post)
        delete_hashtags_from_post(to_delete, post)

    to_add = get_hashtags_to_add(post)
    add_hashtags_to_post(to_add, post)

def get_hashtags_to_add(post):
    new_hashtags = get_hashtags_from_list(post.content.split(' '))
    old_hashtags = [hashtag.title for hashtag in post.hashtag_set.all()]

    return list(set(new_hashtags) - set(old_hashtags))

def get_hashtags_to_delete(post):
    new_hashtags = get_hashtags_from_list(post.content.split(' '))
    old_hashtags = [hashtag.title for hashtag in post.hashtag_set.all()]

    return list(set(old_hashtags) - set(new_hashtags))

def get_hashtags_from_list(words) -> List[str]:
    hashtags = []
    for word in words:
        if word[0] == '#':
            hashtag_title = word[1:]
            hashtags.append(hashtag_title)

    return list(set(hashtags))

def add_hashtags_to_post(hashtags_list, post):
    for hashtag_title in hashtags_list:
        hashtag, created = Hashtag.objects.get_or_create(title=hashtag_title)
        post.hashtag_set.add(hashtag)

def delete_hashtags_from_post(hashtag_list, post):
    for hashtag_title in hashtag_list:
        hashtag, create = Hashtag.objects.get_or_create(title=hashtag_title)
        post.hashtag_set.remove(hashtag)
'''

def process_mentions_from_post_content(post):
    old_mentions = post.mentions.all()

    if old_mentions:
        to_delete = get_mentions_to_delete(post)
        delete_mentions_from_post(to_delete, post)

    to_add = get_mentions_to_add(post)
    add_mentions_to_post(to_add, post)

def get_mentions_to_add(post):
    new_mentions = get_mentions_from_list(post.content.split(' '))
    old_mentions = [mention.username for mention in post.mentions.all()]

    return list(set(new_mentions) - set(old_mentions))

def get_mentions_to_delete(post):
    new_mentions = get_mentions_from_list(post.content.split(' '))
    old_mentions = [mention.username for mention in post.mentions.all()]

    return list(set(old_mentions) - set(new_mentions))

def get_mentions_from_list(words) -> List[str]:
    mentions = []
    for word in words:
        if word[0] == '@':
            username = word[1:]
            if User.objects.filter(username=username):
                mentions.append(username)

    return list(set(mentions))

def add_mentions_to_post(mentions_list, post):
    for mention in mentions_list:
        user = User.objects.get(username=mention)
        post.mentions.add(user)
        update_mention_count_on_profile(user.profile)

def delete_mentions_from_post(mentions_list, post):
    for mention in mentions_list:
        user = User.objects.get(username=mention)
        post.mentions.remove(user)
        update_mention_count_on_profile(user.profile)

def update_mention_count_on_profile(profile):
    profile.mention_count = sum([1 for mention in profile.user.mentions.all()])
    profile.save()

# returns the most mentioned user with the username starting with the argument passed in
def autocomplete_mention_user(mention_start):
    users = User.objects.filter(username__startswith=mention_start).order_by('-profile__mention_count')
    return [user.username for user in users]
