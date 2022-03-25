from django.urls import path
from .views import *
urlpatterns = [

    # POSTS HANDLING

    path('', PostListView.as_view(), name='home'),
    path('post/<str:id>/', PostDetailView.as_view(), name='post-detail'),
    path('post/<str:id>/update/', PostUpdateView.as_view(), name='post-update'),
    path('post/form/create/', PostCreateView.as_view(), name='post-create'),
    path('post/delete/<str:id>/', PostDeleteView.as_view(), name='post-delete'),
    path('post/add/like/<str:id>/', AddLike.as_view(), name='add-like'),
    path('post/remove/like/<str:id>/', AddDislike.as_view(), name='add-dislike'),
    
    # COMMENTS HANDLING

    path('post/comment/delete/<str:id>/', CommentDeleteView.as_view(), name='comment-delete'),
    path('post/comment/edit/<str:id>/', CommentEditView.as_view(), name='comment-edit'),
    path('post/add/comment/like/<str:id>/', AddCommentLike.as_view(), name='add-comment-like'),
    path('post/remove/comment/like/<str:id>/', AddCommentDislike.as_view(), name='add-comment-dislike'),
    path('post/add/comment/reply/<str:post_id>/<str:id>/', CommentReply.as_view(), name='comment-reply'),

    # USER PROFILE/SETTINGS HANDLING

    path('profile/details/<str:username>/', UserDetails.as_view(), name='user-details'),
    path('profile/settings/', settings, name='profile-update'),
    path('profile/<str:username>/', ProfileView.as_view(), name='profile'),
    
    # FOLLOWING/UNFOLLOWING HANDLING

    path('profile/remove/follower/<str:username>/', RemoveFollower.as_view(), name='remove-follower'),
    path('profile/add/follower/<str:username>/', AddFollower.as_view(), name='add-follower'),
    
    # NOTIFICATIONS HANDLING

    path('notification/<str:notification_id>/post/<str:post_id>/', PostNotification.as_view(), name='post-notification'),
    path('notification/<str:notification_id>/profile/<str:username>/', FollowNotification.as_view(), name='follow-notification'),
    path('notification/delete/<str:notification_id>/', RemoveNotification.as_view(), name='notification-delete'),
    path('notification/list/', ListNotifications.as_view(), name='notifications-list'),

    # SEARCH HANDLING

    path('search/results/', SearchResults.as_view(), name='search-results'),
    path('search/', Search.as_view(), name='search'),
    
    # SECURITY & MONETARY FUNCTIONALITIES HANDLING
    
    path('set/key/', key_set.as_view(), name='set-key'),
    path('2fa/conf/', factor_conf.as_view(), name='2fa-conf'),
    path('2fa/conf/done/<str:username>/', factor_done.as_view(), name='2fa-done'),
    path('2fa/conf/cancel/<str:username>/', factor_cancel.as_view(), name='2fa-cancel'),

    # END-TO-END ENCRYPTION FUNCTIONALITIES HANDLING
    
    path('sharedkey/set/<str:touser>', shared_key.as_view(), name='set-sharedkey'),
    path('notes/', notes.as_view(), name='notes'),
    path('list/messages/', messages_list.as_view(), name='messages-list'),
    path('message/', messages_view.as_view(), name='messages'),
    path('delete/note/<str:id>', del_note.as_view(), name='delete-note'),
    
    # OTHER

    path('about/', AboutView.as_view(), name='about'),
    path('more/', more_view.as_view(), name='more'),
]
