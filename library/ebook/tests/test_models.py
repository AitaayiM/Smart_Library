from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from identity.models import User, Role, Roles
from ebook.models import EBook, Review, Category

class EBookModelTestCase(TestCase):
    def setUp(self):
        guest_role = Role.objects.create(name=Roles.GUEST)
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='johndoe@example.com',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password'
        )
        self.user.roles.add(guest_role)

    def test_create_ebook(self):
        ebook = EBook.objects.create(
            author=self.user,
            title='Test Book',
            summary='This is a test summary.',
            pages='100',
            content=SimpleUploadedFile('test_book.pdf', b'file_content'),
            category=Category.MYSTERY
        )
        self.assertEqual(ebook.title, 'Test Book')
        self.assertEqual(ebook.summary, 'This is a test summary.')
        self.assertEqual(ebook.pages, '100')
        self.assertEqual(ebook.category, Category.MYSTERY)
        self.assertEqual(ebook.ratings, 0)
        self.assertTrue(ebook.created_at)
        self.assertTrue(ebook.published_at)

    def test_category_choices(self):
        choices = set(item[0] for item in Category.choices)
        ebook_categories = set(item[0] for item in EBook._meta.get_field('category').choices)
        self.assertTrue(ebook_categories.issubset(choices))

    def test_ebook_string_representation(self):
        ebook = EBook.objects.create(author=self.user, title='Test Book')
        self.assertEqual(str(ebook), 'Test Book')

class ReviewModelTestCase(TestCase):
    def setUp(self):
        guest_role = Role.objects.create(name=Roles.GUEST)
        self.user = User.objects.create_user(
            first_name='John',
            last_name='Doe',
            username='johndoe@example.com',
            date_of_birth='1990-01-01',
            gender='Male',
            password='password'
        )
        self.user.roles.add(guest_role)
        self.ebook = EBook.objects.create(author=self.user, title='Test Book')

    def test_create_review(self):
        review = Review.objects.create(
            ebook=self.ebook,
            user=self.user,
            rating=4,
            comment='This is a test review.'
        )
        self.assertEqual(review.ebook, self.ebook)
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'This is a test review.')

    def test_default_rating_value(self):
        review = Review.objects.create(ebook=self.ebook, user=self.user)
        self.assertEqual(review.rating, 0)

    def test_review_string_representation(self):
        review = Review.objects.create(ebook=self.ebook, user=self.user, comment='Test Review')
        self.assertEqual(str(review), 'Test Book')
