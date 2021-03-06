from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Profile, Notification, Tag, Notes, Message, Keys, Chats
from django.views import View
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileUpdteForm, CommentForm, PostForm
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
from .validations import gpgkeyimport
from users.forms import verification
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib.auth import authenticate

# POSTS HANDLING

class PostListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        logged_in_user = request.user
        ver = verification()
        posts = Post.objects.filter(author__profile__followers__in=[logged_in_user.id]).order_by('likes', '-date_posted')
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
        return response
class PostCreateView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        if request.user.profile.debosited == True:
            ver = verification()
            form = PostForm()
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
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
        return HttpResponseRedirect(request.META['HTTP_REFERER'] + '#' + str(post.id))
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
        return HttpResponseRedirect(request.META['HTTP_REFERER'] + '#' + str(post.id))

# COMMENTS HANDLING

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

# USER PROFILE/SETTINGS HANDLING

@login_required
def settings(request):
    if request.method == 'POST':
        p_form = ProfileUpdteForm(request.POST, request.FILES, instance=request.user.profile)
        if p_form.is_valid():
            profileform = p_form.save(commit=False)
            p_form.name = request.POST.get('name')
            p_form.xmppusername = request.POST.get('xmppusername')
            p_form.xmppserver = request.POST.get('xmppserver')
            p_form.bio = request.POST.get('bio')
            p_form.public_key = request.POST.get('public_key')
            p_form.image = request.POST.get('image')
            if p_form.public_key != '':
                f = open(f'keys/{request.user.username}+{request.user.id}.txt', 'w')
                key = f'''
{p_form.public_key}
                '''
                f.write(key)
                f.close()
                with open(f'keys/{request.user.username}+{request.user.id}.txt', 'rb') as s:
                    armorkey = s.read()
                imprtkey = gpgkeyimport(armorkey)
                if imprtkey != False:
                    profile = request.user.profile
                    profile.fingerprint = str(imprtkey)
                    profile.save()
                    os.remove(f'keys/{request.user.username}+{request.user.id}.txt')
                else:
                    os.remove(f'keys/{request.user.username}+{request.user.id}.txt')
                    messages.warning(request, "Not A PGP Key")
                    return redirect('profile-update')
            profileform.save()
            messages.success(request, f'your account has been updated')
            return redirect('profile', username=request.user)
    else:
        p_form = ProfileUpdteForm(instance=request.user.profile)
    ver = verification()
    context = {'p_form': p_form, "ver": ver}
    return render(request, 'posts/settings.html', context)
class UserDetails(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        ver = verification()
        context = {'user': user, "ver": ver}
        return render(request, 'posts/user_details.html', context)
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
        ver = verification()
        context = {'user': user, 'postscount': postscount, 'ver':ver, 'profile': profile, 'posts': post_list, 'followers_num': followers_num, 'is_following': is_following,}
        return render(request, 'posts/profile.html', context)

# FOLLOWING/UNFOLLOWING HANDLING

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

# SEARCH HANDLING    

class Search(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        return render(request, 'posts/search.html', {"ver": ver})
class SearchResults(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('query')
        if query == '' or query == ' ':
            messages.warning(request, "Why Are You Searching Everything :(")
            return redirect('search')
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
        ver = verification()
        context = {'profilescount': profilescount, "ver": ver, 'postscount': postscount, 'commentscount': commentscount,'profiles': profile_list, 'posts': post_list, 'comments': comment_list,}
        return render(request, 'posts/search_results.html', context)

# NOTIFICATIONS HANDLING

class PostNotification(LoginRequiredMixin, View):
    def get(self, request, notification_id, post_id, *args, **kwargs):
        notification = Notification.objects.get(id=notification_id)
        post = Post.objects.get(id=post_id)
        notification.user_has_seen = True
        notification.save()
        return redirect('post-detail', id=post_id)
class FollowNotification(LoginRequiredMixin, View):
    def get(self, request, notification_id, username, *args, **kwargs):
        notification = Notification.objects.get(id=notification_id)
        user = User.objects.get(username=username)
        profile = user.profile
        notification.user_has_seen = True
        notification.save()
        return redirect('profile', username=username)
class RemoveNotification(LoginRequiredMixin, View):
    def get(self, request, notification_id, *args, **kwargs):
        notification = Notification.objects.get(id=notification_id)
        if notification.to_user == request.user:
            notification.delete()
        return redirect('notifications-list')
class ListNotifications(LoginRequiredMixin, View):
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
        for notification in notifications:
            notification.user_has_seen = True 
            notification.save()
        ver = verification()
        return render(request, "posts/notifications.html", {"ver":ver, 'notifications': notifications_list, 'notificationscount': notificationscount,})

# SECURITY & MONETARY FUNCTIONS HANDLING

class key_set(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'posts/set_key.html')
    def post(self, request, *args, **kwargs):
        return render(request, 'posts/set_key.html')
class factor_conf(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        return render(request, 'posts/2fa_conf.html', {"ver": ver})
class factor_done(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        if request.user == user:
            if request.user.profile.public_key != '' and request.user.profile.fingerprint != '' :
                user.profile.factor_auth = True
                user.save()
                messages.success(request, "2FA Is Now Enabled")
            else:
                messages.success(request, "you have to add a public key and a fingerprint in your settings")
        else:
            return redirect('home')
        return redirect('home')
class factor_cancel(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        if request.user == user:
            user.profile.factor_auth = False
            user.save()
            messages.success(request, "2FA Is Disabled")
        else:
            messages.warning(request, "YOU ARE A HACKER")
        return redirect('home')

# END-TO-END ENCRYPTION FUNCTIONALITIES HANDLING

class notes(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        encprivkey = request.user.profile.privatekey
        pubkey = request.user.profile.publickey
        notes = Notes.objects.filter(author=request.user).order_by('-date')
        response = render(request, 'posts/notes.html', {'privkey': encprivkey, 'notes': notes, 'pubkey': pubkey,"ver": ver})
        return response
    def post(self, request, *args, **kwargs):
        ver = verification()
        notes = Notes.objects.filter(author=request.user).order_by('-date')
        Notes.objects.create(author=request.user, content=request.POST.get('note'))
        encprivkey = request.user.profile.privatekey
        pubkey = request.user.profile.publickey
        response = render(request, 'posts/notes.html', {'privkey': encprivkey, 'notes': notes, 'pubkey': pubkey,"ver": ver})
        return response
class del_note(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        if Notes.objects.filter(id=id).exists():
            note = Notes.objects.get(id=id)
            if request.user == note.author:
                note.delete()
                messages.success(request, 'Note Deleted!')
        return redirect('notes')
class messages_list(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        partners = Chats.objects.get(user=request.user)
        ver = verification()
        context = {'partners': partners, "ver": ver}
        return render(request, 'posts/messages_list.html', context)
class shared_key(LoginRequiredMixin, View):
    def get(self, request, touser, *args, **kwargs):
        user1 = User.objects.get(username=touser)
        if Keys.objects.filter(Q(partner1=user1, partner2=request.user)|Q(partner1=request.user, partner2=user1)).exists():
            response = redirect('messages')
            response['Location'] += f'?username={user1.username}'
            return response 
        elif user1 == request.user:
            messages.warning(request, "Don't Talk To Your Self, I'm worried about you.")
            return redirect('messages-list')
        pubkey1 = request.user.profile.publickey
        pubkey2 = User.objects.get(username=touser)
        return render(request, 'posts/set_shared_key.html', {'pubkey1': pubkey1, 'pubkey2': pubkey2})
    def post(self, request, touser, *args, **kwargs):
        user1 = User.objects.get(username=touser)
        if Keys.objects.filter(Q(partner1=user1, partner2=request.user)|Q(partner1=request.user, partner2=user1)).exists():
            response = redirect('messages')
            response['Location'] += f'?username={user1.username}'
            return response
        elif user1 == request.user:
            messages.warning(request, "Don't Talk To Your Self, I'm worried about you.")
            return redirect('messages-list')
        shared_key1 = request.POST.get('sharedkey1')
        shared_key2 = request.POST.get('sharedkey2')
        Keys.objects.create(partner1=request.user, partner2=user1, shared_key1=shared_key1, shared_key2=shared_key2)
        response = redirect('messages')
        response['Location'] += f'?username={user1.username}'
        chat = Chats.objects.get(user=request.user)
        chat1 = Chats.objects.get(user=user1)
        chat.partners.add(user1) 
        chat1.partners.add(request.user)
        return response
class messages_view(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        if User.objects.filter(username=request.GET.get('username')).exists():
            touser = User.objects.get(username=request.GET.get('username'))
            msgs = Message.objects.filter(Q(to=request.user, author=touser)|Q(author=request.user, to=touser)).order_by('date')
            
            try:
                sharedkey = Keys.objects.get(Q(partner1=touser, partner2=request.user)|Q(partner1=request.user, partner2=touser))
                if sharedkey.partner1 == request.user:
                    shkey = sharedkey.shared_key1
                else:
                    shkey = sharedkey.shared_key2
            except:
                return redirect('set-sharedkey', touser=touser)
            encprivkey = request.user.profile.privatekey
            
            context = {'msgs': msgs, 'privkey': encprivkey, 'sharedkey': shkey, "ver": ver}
        else:
            messages.warning(request, 'User Doesn\'t Exist')
            return redirect('messages-list')
        return render(request, 'posts/messages.html', context)
    def post(self, request, *args, **kwargs):
        ver = verification()
        if User.objects.filter(username=request.GET.get('username')).exists():
            touser = User.objects.get(username=request.GET.get('username'))
            fromuser = request.user
            
            msg = request.POST.get('encryptedmsg')
            if len(msg) < 1:
                pass 
            else:
                createmsg = Message.objects.create(author=fromuser, msg=str(msg), to=touser)
            
            msgs = Message.objects.filter(Q(to=request.user, author=touser)|Q(author=request.user, to=touser)).order_by('date')
            encprivkey = request.user.profile.privatekey
            try:
                sharedkey = Keys.objects.get(Q(partner1=touser, partner2=request.user)|Q(partner1=request.user, partner2=touser))
                if sharedkey.partner1 == request.user:
                    shkey = sharedkey.shared_key1
                else:
                    shkey = sharedkey.shared_key2
            except:
                return redirect('set-sharedkey', touser=touser)

            context = {'msgs': msgs, 'privkey': encprivkey, 'sharedkey': shkey, "ver": ver}
        else:
            messages.warning(request, 'User Doesn\'t Exist')
            return redirect('messages-list')
        return render(request, 'posts/messages.html', context)


# OTHER

class AboutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        return render(request, 'posts/about.html', {"ver": ver})
class more_view(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        ver = verification()
        return render(request, 'posts/more_temp.html', {"ver": ver})