from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Comment, Profile, Notification, Tag, Notes, Message, Keys
from django.views import View
from cryptography.fernet import Fernet
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from .forms import ProfileUpdteForm, CommentForm, PostForm
import hashlib
from mod.models import Txs, Wallet
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import os
from .validations import valid_addr, valid_sig, create_addr, pay, receive, check_addr, check_conf, check_conf_number
from users.forms import verification
from django.urls import reverse_lazy
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.contrib.auth import authenticate
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
        if request.user.profile.debosited == True:
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
                ms.warning(request, 'Wrong Captcha!')
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
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return render(request, 'posts/post_detail.html', context)
class CommentReply(LoginRequiredMixin, View):
    def post(self, request, post_id, id, *args, **kwargs):
        if request.user.profile.debosited == True:
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
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return redirect('post-detail', id=post_id)
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
        if request.user.profile.debosited == True:
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
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return redirect('post-detail', id=new_post.id)
class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        if request.user.profile.debosited == True:
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
        else:
            messages.warning(request, 'You Need To Deposit First')
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
    wallet = Wallet.objects.get(user=request.user)
    context = {'p_form': p_form, 'wallet': wallet,}
    return render(request, 'posts/settings.html', context)
class UserDetails(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        user = User.objects.get(username=username)
        context = {'user': user,}
        return render(request, 'posts/user_details.html', context)
class CommentDeleteView(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        if request.user.profile.debosited == True:
            comment = Comment.objects.get(id=id)
            post = comment.post
            if request.user == comment.author:
                comment.delete()
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return redirect('post-detail', id=post.id)
class CommentEditView(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        if request.user.profile.debosited == True:
            comment = Comment.objects.get(id=id)
            post = comment.post
            if request.user == comment.author:
                comment.content = request.POST.get('content')
                comment.save()
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
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
class PostNotification(LoginRequiredMixin, View):
    def get(self, request, notification_id, post_id, *args, **kwargs):
        if request.user.profile.debosited == True:
            notification = Notification.objects.get(id=notification_id)
            post = Post.objects.get(id=post_id)
            notification.user_has_seen = True
            notification.save()
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return redirect('post-detail', id=post_id)
class FollowNotification(LoginRequiredMixin, View):
    def get(self, request, notification_id, username, *args, **kwargs):
        if request.user.profile.debosited == True:
            notification = Notification.objects.get(id=notification_id)
            user = User.objects.get(username=username)
            profile = user.profile
            notification.user_has_seen = True
            notification.save()
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return redirect('profile', username=username)
class RemoveNotification(LoginRequiredMixin, View):
    def get(self, request, notification_id, *args, **kwargs):
        if request.user.profile.debosited == True:
            notification = Notification.objects.get(id=notification_id)
            if notification.to_user == request.user:
                notification.delete()
            return redirect('notifications-list')
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
class ListNotifications(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if request.user.profile.debosited == True:
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
        else:
            messages.warning(request, 'You Need To Deposit First')
            return redirect('home')
        return render(request, "posts/notifications.html", {'notifications': notifications_list, 'notificationscount': notificationscount,})
class AboutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'posts/about.html')
class factor_conf(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, 'posts/2fa_conf.html')
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
        return redirect('home')

class profile_complete(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        valid = valid_addr(request.user.profile.rec_addr)
        if not valid:
            monero_address = create_addr()
            profile = request.user.profile
            profile.rec_addr = monero_address[0]
            profile.save()
            context = {
                'addr': profile.rec_addr,
            }
        else:
            profile = request.user.profile
            if check_addr(profile.rec_addr):
                context = {
                    'addr': profile.rec_addr,
                }
            else:
                monero_address = create_addr()
                profile = request.user.profile
                profile.rec_addr = monero_address[0]
                profile.save()
                context = {
                    'addr': profile.rec_addr,
                }
        return render(request, 'posts/complete_profile.html', context)
@method_decorator(csrf_exempt, name='dispatch')
class confirm_deposit(LoginRequiredMixin, View):
    #def get(self, request, *args, **kwargs):
    def post(self, request, address, *args, **kwargs):
        txhash = request.POST.get('txhash')
        loc_addr = request.user.profile.rec_addr
        amount = request.POST.get('amount')
        if receive(amount, loc_addr, txhash):
            if check_conf(loc_addr, txhash, amount):
                profile = request.user.profile
                profile.debosited = True
                profile.save()
                transaction = Txs.objects.create(sender=request.user, amnt=float(amount), rec_addr=loc_addr, confs=check_conf_number(loc_addr, txhash, float(amount)), hash=txhash, types='deposit')
                wallet = Wallet.objects.get(user=request.user)
                wallet.balance += float(amount)
                messages.success(request, 'Your Transaction, Is Received, Your Account Is Activated! ')
                return redirect('continue-tx', id=transaction.id)
            else:
                transaction = Txs.objects.create(sender=request.user, amnt=float(amount), rec_addr=loc_addr, confs=check_conf_number(loc_addr, txhash, float(amount)), hash=txhash, types='deposit')
                messages.warning(request, 'Amount Received, but waiting for at least 5 confirmations! check the transaction in your settings')
                return redirect('continue-tx', id=transaction.id)
        else:
            messages.warning(request, 'nothing received, try again')
        return render(request, 'posts/confirm_deposit.html')
class check_deposit(LoginRequiredMixin, View):
    def get(self, request, id, *args, **kwargs):
        transaction = Txs.objects.filter(id=id)
        wallets = Wallet.objects.get(user=request.user)
        if transaction.exists():
            tx = Txs.objects.get(id=id)
            if request.user == tx.sender:
                if tx.types != 'TIP':
                    tx.confs = check_conf_number(tx.rec_addr, tx.hash, tx.amnt)
                    tx.save()
                if tx.confs >= 5:
                    if request.user.profile.debosited == False:
                        profile = request.user.profile
                        profile.debosited = True
                        profile.save()
                        tx.types == 'deposit'
                        tx.save()
                    else:
                        pass
                    if Wallet.objects.filter(trx=tx, user=request.user).exists():
                        pass
                    else:
                        wallets.balance += float(tx.amnt)
                        wallets.trx.add(tx)
                        wallets.save()
            else:
                messages.warning(request, 'TX Doesn\'t Exist')
                return redirect('home')
        else:
            messages.warning(request, 'TX Doesn\'t Exist')
            return redirect('home')
        return render(request, 'posts/continue_tx.html', {'tx': tx,})
class list_txs(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        user = request.user
        transactions = Txs.objects.filter(sender=user)
        tips = Txs.objects.filter(receiver=user)
        wallet = Wallet.objects.get(user=user)
        return render(request, 'posts/list_txs.html', {'txs': transactions, 'tips': tips, 'wallet': wallet,})
class tip_user(LoginRequiredMixin, View):
    def get(self, request, username, *args, **kwargs):
        if User.objects.filter(username=username).exists():
            return render(request, 'posts/tip_user.html', {'touser':username,})
        else:
            messages.warning(request, 'User Doesn\'t Exist')
            return redirect('home')
    def post(self, request, username, *args, **kwargs):
        amount = float(request.POST.get('amnt'))
        fromuser = request.user
        touser = User.objects.get(username=username)
        fromwallet = Wallet.objects.get(user=request.user)
        msg = request.POST.get('txmessage')
        mes = False
        if len(msg) > 2:
            mes = True
        if fromwallet.balance > amount:
            if Wallet.objects.filter(user=touser).exists():
                towallet =  Wallet.objects.get(user=touser)
                fromwallet.balance -= amount
                towallet.balance += amount
                fromwallet.save()
                towallet.save()
                transaction = Txs.objects.create(confs=10, receiver=touser, sender=fromuser, amnt=amount, hash="INTERNAL", types='TIP', rec_addr='INTERNAL')
                if mes == True:
                    transaction.message = msg
                transaction.save()
            else:
                messages.warning(request, 'NONE Existent User')
                return redirect('home')
        else:
            messages.warning(request, 'Insufficient Funds!, Please Deposit into your account or tip the user off platform')
            return redirect('home')
        return redirect('continue-tx', id=transaction.id)
class more_view(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        w = Wallet.objects.get(user=request.user)
        return render(request, 'posts/more_temp.html', {'w':w,})
class notes(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            request.COOKIES['key']
        except:
            return redirect('set-key')
        key = request.COOKIES['key']
        private_key = serialization.load_pem_private_key(bytes(request.user.profile.privatekey, 'utf-8'), password=None)
        notes = Notes.objects.filter(author=request.user).order_by('-date')
        response = render(request, 'posts/notes.html')
        return response
    def post(self, request, *args, **kwargs):
        content = bytes(request.POST.get('content'), 'utf-8').strip()
        if len(content) > 420:
            messages.warning(request, 'Please Do not write more than 420 characters')
            return render(request, 'posts/notes.html', {'content': content,})
        try:
            request.COOKIES['key']
        except:
            return redirect('set-key')
        key = request.COOKIES['key']
        private_key = serialization.load_pem_private_key(bytes(request.user.profile.privatekey, 'utf-8'), password=None)
        public_key = private_key.public_key()
        ciphertext = public_key.encrypt(content, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
        Notes.objects.create(author=request.user, content=ciphertext)
        notes = Notes.objects.filter(author=request.user).order_by('-date')
        response = render(request, 'posts/notes.html')
        return response
class del_note(LoginRequiredMixin, View):
    def post(self, request, id, *args, **kwargs):
        if Notes.objects.filter(id=id).exists():
            note = Notes.objects.get(id=id)
            if request.user == note.author:
                note.delete()
                messages.success(request, 'Note Deleted!')
        return redirect('notes')
class key_set(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            request.COOKIES['key']
            messages.success(request, 'your key is already set.')
            return redirect('home')
        except:
            pass
        return render(request, 'posts/set_key.html')
    def post(self, request, *args, **kwargs):
        try:
            request.COOKIES['key']
            messages.success(request, 'your key is already set.')
            return redirect('home')
        except:
            pass
        password = request.POST.get('password')
        user = authenticate(username=request.user.username,password=password)
        if user:
            response = redirect('home')
            messages.success(request, 'your key is set')
        else:
            messages.warning(request, 'wrong authentication')
            return render(request, 'posts/set_key.html')
        return response
class messages_list(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        mesgs = Message.objects.filter(Q(to=request.user)|Q(author=request.user))
        context = {'msgs': mesgs,}
        return render(request, 'posts/messages_list.html', context)
class shared_key(LoginRequiredMixin, View):
    def get(self, request, touser, *args, **kwargs):
        pubkey1 = request.user.profile.publickey
        pubkey2 = User.objects.get(username=touser)
        return render(request, 'posts/set_shared_key.html', {'pubkey1': pubkey1, 'pubkey2': pubkey2})
    def post(self, request, touser, *args, **kwargs):
        user1 = User.objects.get(username=touser)
        shared_key1 = request.POST.get('sharedkey1')
        shared_key2 = request.POST.get('sharedkey2')
        Keys.objects.create(partner1=request.user, partner2=user1, shared_key1=shared_key1, shared_key2=shared_key2, iv1=request.POST.get('iv1'), iv2=request.POST.get('iv2'))
        response = redirect('messages')
        response['Location'] += f'?username={user1.username}'
        return response
class messages_view(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        if User.objects.filter(username=request.GET.get('username')).exists():
            touser = User.objects.get(username=request.GET.get('username'))
            msgs = Message.objects.filter(Q(to=request.user, author=touser)|Q(author=request.user, to=touser))
            
            try:
                sharedkey = Keys.objects.get(Q(partner1=touser, partner2=request.user)|Q(partner1=request.user, partner2=touser))
                if sharedkey.partner1 == request.user:
                    shkey = sharedkey.shared_key1
                    iv = sharedkey.iv1
                else:
                    shkey = sharedkey.shared_key2
                    iv = sharedkey.iv2
            except:
                return redirect('set-sharedkey', touser=touser)
            # Getting Message Parties's Pub/Priv Keys
            encprivkey = request.user.profile.privatekey
            pubkey = touser.profile.publickey
            
            context = {'msgs': msgs, 'privkey': encprivkey, 'pubkey': pubkey, 'sharedkey': shkey, 'iv': iv,}
        else:
            messages.warning(request, 'User Doesn\'t Exist')
            return redirect('messages-list')
        return render(request, 'posts/messages.html', context)
    def post(self, request, *args, **kwargs):
        if User.objects.filter(username=request.GET.get('username')).exists():
            try:
                request.COOKIES['key']
            except:
                return redirect('set-key')
            
            # Getting Message Parties
            touser = User.objects.get(username=request.GET.get('username'))
            fromuser = request.user
            
            # Creating Message
            msg = request.POST.get('encryptedmsg')
            createmsg = Message.objects.create(author=fromuser, msg=str(msg), to=touser)
            
            # Messages Listing
            msgs = Message.objects.filter(Q(to=request.user, author=touser)|Q(author=request.user, to=touser))
            encprivkey = request.user.profile.privatekey
            pubkey = touser.profile.publickey
            try:
                sharedkey = Keys.objects.get(Q(partner1=touser, partner2=request.user)|Q(partner1=request.user, partner2=touser))
                if sharedkey.partner1 == request.user:
                    shkey = sharedkey.shared_key1
                    iv = sharedkey.iv1
                else:
                    shkey = sharedkey.shared_key2
                    iv = sharedkey.iv2
            except:
                return redirect('set-sharedkey', touser=touser)

            context = {'msgs': msgs, 'privkey': encprivkey, 'pubkey': pubkey, 'sharedkey': shkey, 'iv': iv,}
        else:
            messages.warning(request, 'User Doesn\'t Exist')
            return redirect('messages-list')
        return render(request, 'posts/messages.html', context)