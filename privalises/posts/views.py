from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Profile, Notification, Tag
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileUpdteForm, UserUpdateForm, CommentForm, PostForm
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from .service import process_mentions_from_post_content
import json
class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id]).order_by('-date_posted')
        #posts = Post.objects.all().order_by('-date_posted') 
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 15)
        try:
            post_list = paginator.page(page)
        except PageNotAnInteger:
            post_list = paginator.page(1)
        except EmptyPage:
            post_list = paginator.page(paginator.num_pages)
        form = PostForm()
        context = {'posts': post_list, 'form': form,}
        return render(request, 'posts/post_list.html', context)
    def post(self, request, *args, **kwargs):
        logged_in_user = request.user
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id]).order_by('-date_posted')
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            new_post.create_tags()
            process_mentions_from_post_content(new_post)
        context = {'posts': posts, 'form': form,}
        return render(request, 'posts/post_list.html', context)
@login_required
def PostDetailView(request, pk):
    template_name = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments
    page = request.GET.get('page', 1)
    paginator = Paginator(comments, 15)
    try:
        comment_list = paginator.page(page)
    except PageNotAnInteger:
        comment_list = paginator.page(1)
    except EmptyPage:
        comment_list = paginator.page(paginator.num_pages)
    new_comment = None
    #reply = ReplyForm
    if request.method == 'POST':
        print(request.POST)
        comment_form = CommentForm(data=request.POST)
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.author = User.objects.get(pk=request.user.id)
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
            new_comment.create_tags()
            notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=post.author, post=post)
            # commentToJson = json.dumps(new_comment.toJson(), indent=4)
            return JsonResponse({'comment': new_comment.content, 'date_created': new_comment.date_created, 'author': new_comment.author.username})
    else:
        comment_form = CommentForm()
    return render(request, template_name, {'post': post,'comments': comment_list, 'new_comment': new_comment, 'comment_form': comment_form})
'''
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content', 'image']
    context_object_name = 'content'
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.save()
        process_mentions_from_post_content(form.instance)
        return super().form_valid(form)
'''
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    context_object_name = 'post'
    success_url = '/'
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False    
@login_required
def settings(request):
     if request.method == 'POST':
         u_form = UserUpdateForm(request.POST, instance=request.user)
         p_form = ProfileUpdteForm(request.POST, request.FILES, instance=request.user.profile)
         if u_form.is_valid() and p_form.is_valid():
             u_form.save()
             p_form.save()
             messages.success(request, f'your account has been updated')
             return redirect('home')
     else:
         u_form = UserUpdateForm(instance=request.user)
         p_form = ProfileUpdteForm(instance=request.user.profile)
     context = {'u_form': u_form, 'p_form': p_form}
     return render(request, 'posts/settings.html', context)
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = 'posts/comments_delete.html'
    def get_success_url(self):
        pk = self.kwargs['post_pk']
        return reverse_lazy('post-detail', kwargs={'pk': pk})
    def test_func(self):
        comment = self.get_object()
        if self.request.user == comment.author:
            return True
        return False
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content', 'image']
    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.save()
        process_mentions_from_post_content(form.instance)
        return super().form_valid(form)
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False
class ProfileView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        user = profile.user
        posts = Post.objects.filter(author=user).order_by('-date_posted')
        followers = profile.followers.all()    
        page = request.GET.get('page', 1)
        paginator = Paginator(posts, 2)
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
        followers_num = len(followers)
        context = {'user': user, 'profile': profile, 'posts': post_list, 'followers_num': followers_num, 'is_following': is_following,}
        return render(request, 'posts/profile.html', context)
class RemoveFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        profile.followers.remove(request.user)
        return redirect('profile', pk=profile.pk)
class Search(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        profile_list = Profile.objects.filter(Q(user__username__icontains=query))
        context = {'profiles': profile_list,}
        return render(request, 'posts/search.html', context)
class AddCommentLike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
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
        next = request.POST.get("next", '/')
        return HttpResponseRedirect(next)
class AddCommentDislike(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        comment = Comment.objects.get(pk=pk)
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
        next = request.POST.get("next", '/')
        return HttpResponseRedirect(next)            
class CommentReply(LoginRequiredMixin, View):
    def post(self, request, post_pk, pk, *args, **kwargs):
        post = Post.objects.get(pk=post_pk)
        parent_comment = Comment.objects.get(pk=pk)
        form = CommentForm(request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.post = post
            new_comment.parent = parent_comment
            new_comment.save()
        notification = Notification.objects.create(notification_type=2, from_user=request.user, to_user=parent_comment.author, comment=new_comment)
        return redirect('post-detail', pk=post_pk)
@ login_required
def AddDislike(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        is_like = False
        for like in post.likes.all():
            if like == request.user:
                is_like = True
                break
        if is_like:
            post.likes.remove(request.user)
        is_dislike = False
        if post.dislikes.filter(id=request.user.id).exists():
            post.dislikes.remove(request.user)
            post.like_count += 1
            result = post.like_count
            post.save()
        else:
            post.dislikes.add(request.user)
            post.like_count -= 1
            result = post.like_count
            post.save()
        return JsonResponse({'result': result, })
'''
@login_required
def AddFollower(request):
    result = ''
    id = int(request.POST.get('userid'))
    #user = get_object_or_404(Profile, id=id)
    user = Profile.objects.get(pk=id)
    is_following = False
    for follower in user.followers:
        if follower == request.user:
            is_following = True
            break
    if is_following:
        user.followers.remove(request.user)
    if user.followers.filter(request.user).exists():
        user.followers.remove(request.user)
        user.followers_count -= 1
        result = user.followers_count
        user.save()
    else:
        user.followers.add(request.user)
        user.followers_count += 1
        result = user.followers_count
        user.save()
    return JsonResponse({'result': result, })
'''
@login_required
def AddLike(request):
    if request.POST.get('action') == 'post':
        result = ''
        id = int(request.POST.get('postid'))
        post = get_object_or_404(Post, id=id)
        is_dislike = False
        for dislike in post.dislikes.all():
            if dislike == request.user:
                is_dislike = True
                break
        if is_dislike:
            post.dislikes.remove(request.user)   
        is_like = False
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
            post.like_count -= 1
            result = post.like_count
            post.save()
        else:
            post.likes.add(request.user)
            post.like_count += 1
            result = post.like_count
            post.save()
            notification = Notification.objects.create(notification_type=1, from_user=request.user, to_user=post.author, post=post)
        return JsonResponse({'result': result, })

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
def get_profile_view_by_username(request, username):
    if request.method == 'GET':
        users = User.objects.filter(username=username)
        if users:
            return redirect('profile', pk=users[0].id)
        return redirect('profile', pk=0)
class AddFollower(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        profile = Profile.objects.get(pk=pk)
        profile.followers.add(request.user)
        notification = Notification.objects.create(notification_type=3, from_user=request.user, to_user=profile.user)
        return redirect('profile', pk=profile.pk)
class PostNotification(View):
    def get(self, request, notification_pk, post_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        post = Post.objects.get(pk=post_pk)
        notification.user_has_seen = True
        notification.save()
        return redirect('post-detail', pk=post_pk)
class FollowNotification(View):
    def get(self, request, notification_pk, profile_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        profile = Profile.objects.get(pk=profile_pk)
        notification.user_has_seen = True
        notification.save()
        return redirect('profile', pk=profile_pk)
class RemoveNotification(View):
    def delete(self, request, notification_pk, *args, **kwargs):
        notification = Notification.objects.get(pk=notification_pk)
        notification.user_has_seen = True
        notification.save()
        return HttpResponse('Success', content_type='text/plain')
class ListNotifications(View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(to_user=request.user)
        return render(request, "posts/notifications.html", {'notifications': notifications})