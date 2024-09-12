from django.test import SimpleTestCase
from django.urls import reverse, resolve
from personality.views import (
    create_personal_profile, create_or_add_profile, update_personal_profile,
    delete_personal, delete_profile, create_post, update_post, delete_post,
    get_my_posts, get_my_shared_posts, get_posts_of, get_shared_posts_of,
    like_post, share_post, delete_shared_post, comment_on_post, reply_to_comment,
    update_comment, delete_comment, like_comment, delete_like, send_friendship_invitation,
    delete_friend, get_my_friends, get_friends_of, send_following_invitation,
    unfollow_person, remove_follower, get_my_followers, get_followers_of,
    get_my_followups, get_followups_of, get_invitations, manage_invitation, delete_invitation
)

class PersonalityTestUrls(SimpleTestCase):

    def test_create_personal_profile_url_resolves(self):
        url = reverse('create_profile')
        self.assertEqual(resolve(url).func, create_personal_profile)

    def test_create_or_add_profile_url_resolves(self):
        url = reverse('add_profile')
        self.assertEqual(resolve(url).func, create_or_add_profile)

    def test_update_personal_profile_url_resolves(self):
        url = reverse('update_profile')
        self.assertEqual(resolve(url).func, update_personal_profile)

    def test_delete_personal_url_resolves(self):
        url = reverse('delete_personal')
        self.assertEqual(resolve(url).func, delete_personal)

    def test_delete_profile_url_resolves(self):
        url = reverse('delete_profile')
        self.assertEqual(resolve(url).func, delete_profile)

    def test_create_post_url_resolves(self):
        url = reverse('create_post')
        self.assertEqual(resolve(url).func, create_post)

    def test_update_post_url_resolves(self):
        url = reverse('update_post', args=['1'])
        self.assertEqual(resolve(url).func, update_post)

    def test_delete_post_url_resolves(self):
        url = reverse('delete_post', args=['1'])
        self.assertEqual(resolve(url).func, delete_post)

    def test_get_my_posts_url_resolves(self):
        url = reverse('get_my_posts')
        self.assertEqual(resolve(url).func, get_my_posts)

    def test_get_my_shared_posts_url_resolves(self):
        url = reverse('get_my_shared_posts')
        self.assertEqual(resolve(url).func, get_my_shared_posts)

    def test_get_posts_of_url_resolves(self):
        url = reverse('get_posts_of', args=['1'])
        self.assertEqual(resolve(url).func, get_posts_of)

    def test_get_shared_posts_of_url_resolves(self):
        url = reverse('get_shared_posts_of', args=['1'])
        self.assertEqual(resolve(url).func, get_shared_posts_of)

    def test_like_post_url_resolves(self):
        url = reverse('like_post', args=['1'])
        self.assertEqual(resolve(url).func, like_post)

    def test_share_post_url_resolves(self):
        url = reverse('share_post', args=['1'])
        self.assertEqual(resolve(url).func, share_post)

    def test_delete_shared_post_url_resolves(self):
        url = reverse('delete_share', args=['1'])
        self.assertEqual(resolve(url).func, delete_shared_post)

    def test_comment_on_post_url_resolves(self):
        url = reverse('comment_on_post', args=['1'])
        self.assertEqual(resolve(url).func, comment_on_post)

    def test_reply_to_comment_url_resolves(self):
        url = reverse('reply_to_comment', args=['1'])
        self.assertEqual(resolve(url).func, reply_to_comment)

    def test_update_comment_url_resolves(self):
        url = reverse('update_comment', args=['1'])
        self.assertEqual(resolve(url).func, update_comment)

    def test_delete_comment_url_resolves(self):
        url = reverse('delete_comment', args=['1'])
        self.assertEqual(resolve(url).func, delete_comment)

    def test_like_comment_url_resolves(self):
        url = reverse('like_comment', args=['1'])
        self.assertEqual(resolve(url).func, like_comment)

    def test_delete_like_url_resolves(self):
        url = reverse('delete_like', args=['1'])
        self.assertEqual(resolve(url).func, delete_like)

    def test_send_friendship_invitation_url_resolves(self):
        url = reverse('send_friendship_invitation', args=['1'])
        self.assertEqual(resolve(url).func, send_friendship_invitation)

    def test_delete_friend_url_resolves(self):
        url = reverse('delete_friend', args=['1'])
        self.assertEqual(resolve(url).func, delete_friend)

    def test_get_my_friends_url_resolves(self):
        url = reverse('get_my_friends')
        self.assertEqual(resolve(url).func, get_my_friends)

    def test_get_friends_of_url_resolves(self):
        url = reverse('get_friends_of', args=['1'])
        self.assertEqual(resolve(url).func, get_friends_of)

    def test_send_following_invitation_url_resolves(self):
        url = reverse('send_following_invitation', args=['1'])
        self.assertEqual(resolve(url).func, send_following_invitation)

    def test_unfollow_person_url_resolves(self):
        url = reverse('unfollow_person', args=['1'])
        self.assertEqual(resolve(url).func, unfollow_person)

    def test_remove_follower_url_resolves(self):
        url = reverse('remove_follower', args=['1'])
        self.assertEqual(resolve(url).func, remove_follower)

    def test_get_my_followers_url_resolves(self):
        url = reverse('get_my_followers')
        self.assertEqual(resolve(url).func, get_my_followers)

    def test_get_followers_of_url_resolves(self):
        url = reverse('get_followers_of', args=['1'])
        self.assertEqual(resolve(url).func, get_followers_of)

    def test_get_my_followups_url_resolves(self):
        url = reverse('get_my_followups')
        self.assertEqual(resolve(url).func, get_my_followups)

    def test_get_followups_of_url_resolves(self):
        url = reverse('get_followups_of', args=['1'])
        self.assertEqual(resolve(url).func, get_followups_of)

    def test_get_invitations_url_resolves(self):
        url = reverse('get_invitations')
        self.assertEqual(resolve(url).func, get_invitations)

    def test_manage_invitation_url_resolves(self):
        url = reverse('manage_invitation', args=['1'])
        self.assertEqual(resolve(url).func, manage_invitation)

    def test_delete_invitation_url_resolves(self):
        url = reverse('delete_invitation', args=['1'])
        self.assertEqual(resolve(url).func, delete_invitation)
