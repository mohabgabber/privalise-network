from django.urls import path
#from django.conf import settings
#from django.conf.urls.static import static
from .views import CommentEditView, AddLike, AddDislike, SearchResults, UserDetails, AddFavourites, RemoveNotification, ListNotifications, PostNotification, FollowNotification,  Search, AddCommentLike, AddCommentDislike, ProfileView, settings, AddFollower, RemoveFollower, PostListView, PostCreateView, PostDetailView, PostUpdateView, PostDeleteView, CommentDeleteView
urlpatterns = [
    path('', PostListView.as_view(), name='home'),
    path('profile/details/<str:username>/', UserDetails.as_view(), name='user-details'),
    path('post/<str:id>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<str:id>/update/', PostUpdateView.as_view(), name='post-update'),
    path('profile/settings/', settings, name='profile-update'),
    path('post/delete/<str:id>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/comment/delete/<str:id>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/comment/edit/<str:id>', CommentEditView.as_view(), name='comment-edit'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    path('profile/remove/follower/<str:username>/', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/add/follower/<str:username>/', AddFollower.as_view(), name='add-follower'),
    path('post/add/like/<str:id>', AddLike.as_view(), name='add-like'),
    path('post/add/comment/like/<str:id>/', AddCommentLike.as_view(), name='add-comment-like'),
    path('post/remove/comment/like/<str:id>/', AddCommentDislike.as_view(), name='add-comment-dislike'),
    #path('post/add/comment/reply/<int:post_pk>/<int:pk>/', CommentReply.as_view(), name='add-comment-reply'),
    path('post/remove/like/<str:id>', AddDislike.as_view(), name='add-dislike'),
    path('search/', Search.as_view(), name='search'),
    path('search/results', SearchResults.as_view(), name='search-results'),
    path('fav/add/<str:id>/', AddFavourites, name='add-fav'),
    path('post/create', PostCreateView.as_view(), name='post-create'),
    path('notification/<str:notification_id>/post/<str:post_id>/', PostNotification.as_view(), name='post-notification'),
    path('notification/<str:notification_id>/profile/<str:username>/', FollowNotification.as_view(), name='follow-notification'),
    path('notification/delete/<str:notification_id>/', RemoveNotification.as_view(), name='notification-delete'),
    path('notification/list/', ListNotifications.as_view(), name='notifications-list'),

]
