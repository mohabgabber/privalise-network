from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Profile, Notification, Tag, About
from django.views import View
from django.http import HttpResponseRedirect
from monero.address import address 
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileUpdteForm, CommentForm, PostForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
#from .xmrscript import create_addr, pay, receive, check_addr, check_conf, valid_addr
from users.forms import verification
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        ver = verification()
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id]).order_by('-date_posted')
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 20)
        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            post_list = paginator.page(paginator.num_pages)
        postscount = posts.count()
        #form = PostForm()
        context = {'posts': post_list, 'postscount': postscount, 'ver': ver,}
        response = render(request, 'posts/post_list.html', context)
        response.set_cookie('admin', 'True', 5)
        return response
class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id)
        form = CommentForm()
        ver = verification()
        comments = Comment.objects.filter(post=post)
        commentcount = 0
        for comment in comments:
            commentcount += 1
        likes = post.likes.count() - post.dislikes.count()
        page = request.GET.get('page', 1)
        paginator = Paginator(comments, 20)
        try:
            comments_list = paginator.page(page)
        except PageNotAnInteger:
            comments_list = paginator.page(1)
        except EmptyPage:
            comments_list = paginator.page(paginator.num_pages)

        context = {
            'likes': likes,
            'post': post,
            'form': form,
            'ver': ver,
            'commentcount': commentcount,
            'comments': comments_list,
        }
        return render(request, 'posts/post_detail.html', context)
    def post(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id)
        form = CommentForm(request.POST)
        valid = True
        ver = verification(request.POST)
        if form.is_valid() and ver.is_valid():
            new_comment = form.save(commit=False)
            new_comment.content = request.POST.get('content')
            new_comment.author = request.user
            new_comment.post = post
            new_comment.save()
            new_comment.create_tags()

            if new_comment.author == new_comment.post.author:
                pass
            else:
                notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)
        else:
            ver = verification()
            valid = False
            comment_content = request.POST.get('content')
            messages.warning(request, 'Wrong Captcha!')
        comments = Comment.objects.filter(post=post)
        commentcount = 0
        for comment in comments:
            commentcount += 1
        likes = post.likes.count() - post.dislikes.count()
        page = request.GET.get('page', 1)
        paginator = Paginator(comments, 20)
        try:
            comments_list = paginator.page(page)
        except PageNotAnInteger:
            comments_list = paginator.page(1)
        except EmptyPage:
            comments_list = paginator.page(paginator.num_pages)
        if not valid:
            context = {
                'likes': likes,
                'post': post,
                'ver': ver,
                'form': form,
                'comment_content': comment_content,
                'commentcount': commentcount,
                'comments': comments_list,
            }
        else:
            context = {
                'likes': likes,
                'post': post,
                'ver': ver,
                'form': form,
                'commentcount': commentcount,
                'comments': comments_list,
            }
        return render(request, 'posts/post_detail.html', context)
class CommentReply(LoginRequiredMixin, View):
    def post(self, request, post_id, id, *args, **kwargs):
        post = Post.objects.get(id=post_id)
        parent_comment = Comment.objects.get(id=id)
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()
        if new_comment.author == new_comment.post.author or new_comment.author == parent_comment.author:
            pass
        else:
            notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)
        return redirect('post-detail', id=post_id)
class PostCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        form = PostForm()
        context = {'form': form, 'ver': ver,}
        return render(request, 'posts/post_form.html', context)
    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        ver = verification(request.POST)
        if form.is_valid() and ver.is_valid():
            new_post = form.save(commit=False)
            new_post.content = request.POST.get('content').strip()
            new_post.author = request.user
            new_post.save()
            new_post.create_tags()
        else:
            ver = verification()
            content = request.POST.get('content')
            messages.warning(request, 'Wrong Captcha!')
            return render(request, 'posts/post_form.html', {'content': content, 'ver': ver,})
        context = {'form': form, 'ver': ver,}
        return redirect('post-detail', id=new_post.id)
class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id)
        if post:
            if request.user == post.author:
                post.delete()
                messages.success(request, 'Post Deleted!')
                return redirect('home')
            else:
                return redirect('home')
        else:
            return redirect('home')
@login_required
def settings(request):
    if request.method == 'POST':
        p_form = ProfileUpdteForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            profileform = p_form.save(commit=False)
            p_form.name = request.POST.get('name')
            p_form.xmppusername = request.POST.get('xmppusername')
            p_form.xmppserver = request.POST.get('xmppserver')
            p_form.monero = request.POST.get('monero')
            p_form.bio = request.POST.get('bio')
            p_form.public_key = request.POST.get('public_key')
            p_form.image = request.POST.get('image')
            p_form.fingerprint = request.POST.get('fingerprint')
            if p_form.public_key != '' and p_form.fingerprint == '':
                messages.warning(request, f'You Can\'t Add Public Key Without It\'s FingerPrint')
                return redirect('profile-update')
            elif p_form.public_key == '' and p_form.fingerprint != '':
                messages.warning(request, f'You Can\'t Add FingerPrint Without It\'s Public Key')
                return redirect('profile-update')
            if p_form.public_key != '':
                f = open(f'keys/{request.user.username}+{request.user.id}.txt', 'w')
                key = f'''
{p_form.public_key}
                '''
                f.write(key)
                f.close()
                pgp = os.popen(f'gpg --import keys/{request.user.username}+{request.user.id}.txt')
            if p_form.monero == '':
                p_form.save()
                messages.success(request, f'your account has been updated')
                return redirect('profile', username=request.user)
            elif valid_addr(p_form.monero):
                p_form.save()
                messages.success(request, f'your account has been updated')
                return redirect('profile', username=request.user)
            else:
                messages.warning(request, f'monero address isn\'t correct')
                return redirect('profile-update')
    else:
        p_form = ProfileUpdteForm(instance=request.user.profile)
    context = {'p_form': p_form,}
    return render(request, 'posts/settings.html', context)
class UserDetails(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        context = {'user': user,}
        return render(request, 'posts/user_details.html', context)
class CommentDeleteView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        comment = Comment.objects.get(id=id)
        post = comment.post
        if request.user == comment.author:
            comment.delete()
        return redirect('post-detail', id=post.id)
class CommentEditView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        comment = Comment.objects.get(id=id)
        post = comment.post
        if request.user == comment.author:
            comment.content = request.POST.get('content')
            comment.save()
        return redirect('post-detail', id=post.id)
class PostUpdateView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id)
        if post:
            if request.user == post.author:
                post.content = request.POST.get('content')
                post.save()
                messages.success(request, 'Post Updated Succesfully')
                return redirect('post-detail', id=id)
            else:
                return redirect('home')
        else:
            return redirect('home')
class ProfileView(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        profile = user.profile
        posts = Post.objects.filter(author=user).order_by('-date_posted')
        followers = profile.followers.all()    
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 20)
        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            post_list = paginator.page(paginator.num_pages)
        if len(followers) == 0:
            is_following = False
        for follower in followers:
            if follower == request.user:
                is_following = True
                break
            else:
                is_following = False
        postscount = posts.count()
        followers_num = len(followers)
        context = {'user': user, 'postscount': postscount, 'profile': profile, 'posts': post_list, 'followers_num': followers_num, 'is_following': is_following,}
        return render(request, 'posts/profile.html', context)
class AddFollower(LoginRequiredMixin, View):
    def post(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        profile = user.profile
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=user)
        return redirect('profile', username=user.username)
class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        profile = user.profile
        profile.followers.remove(request.user)
        return redirect('profile', username=user.username)    
class Search(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'posts/search.html')
class SearchResults(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profiles = Profile.objects.filter(Q(user__username__icontains=query))
        posts = Post.objects.filter(Q(content__icontains=query))
        comments = Comment.objects.filter(Q(content__icontains=query))
        
        postspage = request.GET.get('posts', 1)
        postspaginator = Paginator(posts, 20)
        try:
            post_list = postspaginator.page(postspage)
        except PageNotAnInteger:
            post_list = postspaginator.page(1)
        except EmptyPage:
            post_list = postspaginator.page(postspaginator.num_pages)
        
        commentspage = request.GET.get('comments', 1)
        commentspaginator = Paginator(comments, 20)
        try:
            comment_list = commentspaginator.page(commentspage)
        except PageNotAnInteger:
            comment_list = commentspaginator.page(1)
        except EmptyPage:
            comment_list = commentspaginator.page(commentspaginator.num_pages)
        
        profilespage = request.GET.get('profiles', 1)
        profilepaginator = Paginator(profiles, 20)
        try:
            profile_list = profilepaginator.page(profilespage)
        except PageNotAnInteger:
            profile_list = profilepaginator.page(1)
        except EmptyPage:
            profile_list = profilepaginator.page(profilepaginator.num_pages)
        commentscount = comments.count()
        postscount = posts.count()
        profilescount = profiles.count()
        context = {'profilescount': profilescount, 'postscount': postscount, 'commentscount': commentscount,'profiles': profile_list, 'posts': post_list, 'comments': comment_list,}
        return render(request, 'posts/search_results.html', context)    
class AddCommentLike(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        comment = Comment.objects.get(id=id)
        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if is_dislike:
            comment.dislikes.remove(request.user)
        is_like = False
        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            comment.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=comment.author, comment=comment)
        if is_like:
            comment.likes.remove(request.user)
        comment.likescount = comment.likes.count() - comment.dislikes.count()
        return redirect('post-detail', id=comment.post.id)
class AddCommentDislike(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        comment = Comment.objects.get(id=id)
        is_like = False
        for like in comment.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            comment.likes.remove(request.user)
        is_dislike = False
        for dislike in comment.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            comment.dislikes.add(request.user)
        if is_dislike:
            comment.dislikes.remove(request.user)
        comment.likescount = comment.likes.count() - comment.dislikes.count()
        return redirect('post-detail', id=comment.post.id)
class AddLike(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id)
        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if is_dislike:
            post.dislikes.remove(request.user)  
        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if not is_like:
            post.likes.add(request.user)
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)
        if is_like:
            post.likes.remove(request.user)
        return redirect('post-detail', id=id)
class AddDislike(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        post = Post.objects.get(id=id)
        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)
        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if not is_dislike:
            post.dislikes.add(request.user)
        if is_dislike:
            post.dislikes.remove(request.user)
        return redirect('post-detail', id=id)        
@login_required
def FavouritesList(request):
    new = Post.newmanager.filter(favourites=request.user)
    return render(request, 'accounts/favourites.html', {'new': new})
@login_required
def AddFavourites(request, id):
    post = get_object_or_404(Post, id=id)
    if post.favourites.filter(id=request.user.id).exists():
        post.favourites.remove(request.user)
        messages.success(request, f'Post Is UnMarkaLised :( Maybe It\'s For The Better')
    else:
        post.favourites.add(request.user)
        messages.success(request, f'Post Is MarkaLised! Amazing :D')
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
class PostNotification(View):
    def get(self, request, notification_id, post_id, *args, **kwargs):
        notification = Notification.objects.get(id=notification_id)
        post = Post.objects.get(id=post_id)
        notification.user_has_seen = True
        notification.save()
        return redirect('post-detail', id=post_id)
class FollowNotification(View):
    def get(self, request, notification_id, username, *args, **kwargs):
        notification = Notification.objects.get(id=notification_id)
        user = User.objects.get(username=username)
        profile = user.profile
        notification.user_has_seen = True
        notification.save()
        return redirect('profile', username=username)
class RemoveNotification(View):
    def get(self, request, notification_id, *args, **kwargs):
        notification = Notification.objects.get(id=notification_id)
        if notification.to_user == request.user:
            notification.delete()
        return redirect('notifications-list')
class ListNotifications(View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(to_user=request.user)
        page = request.GET.get('page', 1)
        paginator = Paginator(notifications, 10)
        try:
            notifications_list = paginator.page(page)
        except PageNotAnInteger:
            notifications_list = paginator.page(1)
        except EmptyPage:
            notifications_list = paginator.page(paginator.num_pages)
        notificationscount = notifications.count()
        return render(request, "posts/notifications.html", {'notifications': notifications_list, 'notificationscount': notificationscount,})
class AboutView(View):
    def get(self, request, *args, **kwargs):
        about = About.objects.get(id=1)
        return render(request, 'posts/about.html', {'about': about,})
class factor_conf(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'posts/2fa_conf.html')
class factor_done(View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        if request.user == user:
            user.profile.factor_auth = True
            user.save()
            messages.success(request, "2FA Is Now Enabled")
        return redirect('home')
class factor_cancel(View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        if request.user == user:
            user.profile.factor_auth = False
            user.save()
            messages.success(request, "2FA Is Disabled")
        return redirect('home')