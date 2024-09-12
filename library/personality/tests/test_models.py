from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from personality.models import Personal, Post, Comment, Share, Like, Reaction, Invitation, Friendship, Following

User = get_user_model()

class PersonalityModelTests(TestCase):

    def setUp(self):
        # Create User instances
        self.user1 = User.objects.create_user(
            username='user1@example.com',
            first_name='User',
            last_name='One',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            username='user2@example.com',
            first_name='User',
            last_name='Two',
            date_of_birth='1992-02-02',
            gender='Female',
            password='password123'
        )

        # Create Personal instances
        self.personal1 = Personal.objects.create(
            user=self.user1,
            image=SimpleUploadedFile(name='test_image1.jpg', content=b'', content_type='image/jpeg'),
            phone='1234567890',
            about_us='About user one',
            country='Country1',
            isbn='1234567890123'
        )
        self.personal2 = Personal.objects.create(
            user=self.user2,
            image=SimpleUploadedFile(name='test_image2.jpg', content=b'', content_type='image/jpeg'),
            phone='0987654321',
            about_us='About user two',
            country='Country2',
            isbn='1234567890124'
        )

        # Create Post instance
        self.post = Post.objects.create(
            personal=self.personal1,
            content='This is a post',
            image=SimpleUploadedFile(name='post_image.jpg', content=b'', content_type='image/jpeg')
        )

        # Create Comment instance
        self.comment = Comment.objects.create(
            personal=self.personal1,
            post=self.post,
            content='This is a comment',
            image=SimpleUploadedFile(name='comment_image.jpg', content=b'', content_type='image/jpeg')
        )

        # Create Share instance
        self.share = Share.objects.create(
            personal=self.personal1,
            post=self.post
        )

        # Create Like instance
        self.like = Like.objects.create(
            personal=self.personal1,
            post=self.post
        )

        # Create Reaction instance
        self.reaction = Reaction.objects.create(
            personal=self.personal1,
            post=self.post,
            type='Like'
        )

        # Create Invitation instance
        self.invitation = Invitation.objects.create(
            from_personal=self.personal1,
            to_personal=self.personal2,
            type='Friendship'
        )

        # Create Friendship instance
        self.friendship = Friendship.objects.create(
            personal=self.personal1,
            friend=self.personal2
        )

        # Create Following instance
        self.following = Following.objects.create(
            follower=self.personal1,
            followed_personal=self.personal2
        )

    def test_personal_creation(self):
        self.assertEqual(str(self.personal1), f"{self.user1.first_name} {self.user1.last_name}")
        self.assertEqual(self.personal1.user, self.user1)
        self.assertEqual(self.personal1.phone, '1234567890')
        self.assertEqual(self.personal1.about_us, 'About user one')
        self.assertEqual(self.personal1.country, 'Country1')
        self.assertEqual(self.personal1.isbn, '1234567890123')

    def test_post_creation(self):
        self.assertEqual(self.post.personal, self.personal1)
        self.assertEqual(self.post.content, 'This is a post')
        self.assertIsNotNone(self.post.image)

    def test_comment_creation(self):
        self.assertEqual(self.comment.personal, self.personal1)
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.content, 'This is a comment')
        self.assertIsNotNone(self.comment.image)

    def test_share_creation(self):
        self.assertEqual(self.share.personal, self.personal1)
        self.assertEqual(self.share.post, self.post)

    def test_like_creation(self):
        self.assertEqual(self.like.personal, self.personal1)
        self.assertEqual(self.like.post, self.post)

    def test_reaction_creation(self):
        self.assertEqual(self.reaction.personal, self.personal1)
        self.assertEqual(self.reaction.post, self.post)
        self.assertEqual(self.reaction.type, 'Like')

    def test_invitation_creation(self):
        self.assertEqual(self.invitation.from_personal, self.personal1)
        self.assertEqual(self.invitation.to_personal, self.personal2)
        self.assertEqual(self.invitation.type, 'Friendship')
        self.assertEqual(self.invitation.status, 'Pending')

    def test_friendship_creation(self):
        self.assertEqual(self.friendship.personal, self.personal1)
        self.assertEqual(self.friendship.friend, self.personal2)

    def test_following_creation(self):
        self.assertEqual(self.following.follower, self.personal1)
        self.assertEqual(self.following.followed_personal, self.personal2)
