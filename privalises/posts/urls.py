from django.urls import path
#from django.conf import settings
#from django.conf.urls.static import static
from .views import UserDetails, AddFavourites, RemoveNotification, ListNotifications, PostNotification, FollowNotification,  Search, AddCommentLike, AddCommentDislike, ProfileView, settings, AddFollower, RemoveFollower, PostListView, PostCreateView, PostDetailView, PostUpdateView, PostDeleteView, CommentDeleteView
urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('profile/details/<str:username>/', UserDetails.as_view(), name='user-details'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    path('profile/settings/', settings, name='profile-update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('post/<int:post_pk>/comment/delete/<int:pk>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/remove/follower/<str:username>/', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/add/follower/<str:username>/', AddFollower.as_view(), name='add-follower'),
    #path('post/add/like/', AddLike, name='add-like'),
    path('post/remove/comment/like/<int:post_pk>/<int:pk>/', AddCommentLike.as_view(), name='add-comment-like'),
    path('post/add/comment/like/<int:post_pk>/<int:pk>/', AddCommentDislike.as_view(), name='add-comment-dislike'),
    #path('post/add/comment/reply/<int:post_pk>/<int:pk>/', CommentReply.as_view(), name='add-comment-reply'),
    #path('post/remove/like/', AddDislike, name='add-dislike'),
    path('search/', Search.as_view(), name='search'),
    path('fav/add/<int:id>/', AddFavourites, name='add-fav'),
    path('post/create', PostCreateView.as_view(), name='post-create'),
    path('notification/<int:notification_pk>/post/<int:post_pk>/', PostNotification.as_view(), name='post-notification'),
    path('notification/<int:notification_pk>/profile/<str:username>/', FollowNotification.as_view(), name='follow-notification'),
    path('notification/delete/<int:notification_pk>/', RemoveNotification.as_view(), name='notification-delete'),
    path('notification/list/', ListNotifications.as_view(), name='notifications-list'),

]
