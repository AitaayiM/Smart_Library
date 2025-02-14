from django.urls import path
from .views import create_personal_profile, update_personal_profile, delete_personal, delete_profile, create_post, create_or_add_profile, update_post, delete_post, comment_on_post, reply_to_comment, update_comment, delete_comment, like_post, like_comment, delete_like, share_post, delete_shared_post, send_friendship_invitation, send_following_invitation, manage_invitation, delete_invitation, unfollow_person, remove_follower, delete_friend, get_my_posts, get_my_shared_posts, get_posts_of, get_shared_posts_of, get_my_friends, get_friends_of, get_my_followers, get_followers_of, get_my_followups, get_followups_of, get_invitations

urlpatterns = [
    path('profile/create', create_personal_profile, name='create_profile'),
    path('profile/add', create_or_add_profile, name='add_profile'),
    path('profile/update', update_personal_profile, name='update_profile'),
    path('profile/delete', delete_personal, name='delete_personal'),
    path('profile/remove', delete_profile, name='delete_profile'),
    path('post/create', create_post, name='create_post'),
    path('post/update/<str:pk>', update_post, name='update_post'),
    path('post/delete/<str:pk>', delete_post, name='delete_post'),
    path('post/myall', get_my_posts, name='get_my_posts'),
    path('post/share/myall', get_my_shared_posts, name='get_my_shared_posts'),
    path('post/allof/<str:pk>', get_posts_of, name='get_posts_of'),
    path('post/share/allof/<str:pk>', get_shared_posts_of, name='get_shared_posts_of'),
    path('post/like/<str:post_id>', like_post, name='like_post'),
    path('post/share/create/<str:post_id>', share_post, name='share_post'),
    path('post/share/delete/<str:pk>', delete_shared_post, name='delete_share'),
    path('post/comment/create/<str:post_id>', comment_on_post, name='comment_on_post'),
    path('post/comment/reply/<str:comment_id>', reply_to_comment, name='reply_to_comment'),
    path('post/comment/update/<str:pk>', update_comment, name='update_comment'),
    path('post/comment/delete/<str:pk>', delete_comment, name='delete_comment'),
    path('post/comment/like/<str:comment_id>', like_comment, name='like_comment'),
    path('reaction/delete/<str:pk>', delete_like, name='delete_like'),
    path('friendship/send/<str:to_personal_id>', send_friendship_invitation, name='send_friendship_invitation'),
    path('friendship/delete/<str:friend_id>', delete_friend, name='delete_friend'),
    path('friendship/myall', get_my_friends, name='get_my_friends'),
    path('friendship/allof/<str:pk>', get_friends_of, name='get_friends_of'),
    path('following/send/<str:to_personal_id>', send_following_invitation, name='send_following_invitation'),
    path('following/unfollow/<str:personal_id>', unfollow_person, name='unfollow_person'),
    path('following/remove/<str:personal_id>', remove_follower, name='remove_follower'),
    path('following/follower/myall', get_my_followers, name='get_my_followers'),
    path('following/follower/allof/<str:pk>', get_followers_of, name='get_followers_of'),
    path('following/followup/myall', get_my_followups, name='get_my_followups'),
    path('following/followup/allof/<str:pk>', get_followups_of, name='get_followups_of'),
    path('invitation/all', get_invitations, name='get_invitations'),
    path('invitation/manage/<str:invitation_id>', manage_invitation, name='manage_invitation'),
    path('invitation/delete/<str:pk>', delete_invitation, name='delete_invitation'),
] 
