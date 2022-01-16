from django.test import TestCase
from django.contrib.auth.models import User
from .models import Post, Profile
from . import service

# Create your tests here.

# Test case for mention service functions
class MentionTestCase(TestCase):

    def setUp(self):
        pass

    def test_get_mentions_from_list(self):
        User.objects.create(username='bob', password='password', email='bob@example.com')
        User.objects.create(username='jen', password='password', email='jen@example.com')
        User.objects.create(username='chris', password='password', email='chris@example.com')
        words = ['@bob', 'please', 'tell', '@jen', 'and', '@jane', 'that', '@chris', 'has', 'their', 'phones']
        mentions_list = service.get_mentions_from_list(words)

        self.assertEqual(mentions_list, list(set(['bob', 'jen', 'chris'])))

    def test_get_mentions_to_add(self):
        user = User.objects.create(username='user', password='password', email='user@example.com')
        user_a = User.objects.create(username='a', password='password', email='a@example.com')
        user_b = User.objects.create(username='b', password='password', email='b@example.com')
        user_c = User.objects.create(username='c', password='password', email='c@example.com')
        user_d = User.objects.create(username='d', password='password', email='d@example.com')
        user_e = User.objects.create(username='e', password='password', email='e@example.com')

        post = Post.objects.create(content='@c @d @e', author=user)
        post.mentions.add(user_a, user_b, user_c)

        to_add = service.get_mentions_to_add(post)

        self.assertEqual(sorted(to_add), ['d', 'e'])

    def test_get_mentions_to_delete(self):
        user = User.objects.create(username='user', password='password', email='user@example.com')
        user_a = User.objects.create(username='a', password='password', email='a@example.com')
        user_b = User.objects.create(username='b', password='password', email='b@example.com')
        user_c = User.objects.create(username='c', password='password', email='c@example.com')
        user_d = User.objects.create(username='d', password='password', email='d@example.com')
        user_e = User.objects.create(username='e', password='password', email='e@example.com')

        post = Post.objects.create(content='@c @d @e', author=user)
        post.mentions.add(user_a, user_b, user_c)

        to_delete = service.get_mentions_to_delete(post)

        self.assertEqual(sorted(to_delete), ['a', 'b'])

    def test_update_mention_count_on_profile(self):
        ken = User.objects.create(username='ken', email='ken@example.com', password='password')
        joe = User.objects.create(username='joe', email='joe@example.com', password='password')
        profile = joe.profile

        for i in range(0, 3):
            post = Post.objects.create(content='', author=ken)
            post.mentions.add(joe)

        service.update_mention_count_on_profile(profile)

        self.assertEqual(profile.mention_count, 3)

    def test_autocomplete_mention_user(self):
        bill = User.objects.create(username='bill', email='bill@example.com', password='password')
        beatrice = User.objects.create(username='beatrice', email='beatrice@example.com', password='password')
        profile = beatrice.profile

        post = Post.objects.create(content='', author=bill)
        post.mentions.add(beatrice)
        profile.mention_count = 1
        profile.save()

        autocomplete = service.autocomplete_mention_user('b')

        self.assertEqual(autocomplete, ['beatrice', 'bill'])

