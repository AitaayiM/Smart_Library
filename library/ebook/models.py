from django.db import models
from identity.models import User
# Create your models here.
class Category(models.TextChoices):

    MYSTERY = 'Mystery'
    Romance = 'Romance'
    FICTION = 'Science Fiction'
    FANTASY = 'Fantasy'
    THRILLER = 'Thriller'
    HISTORICAL_FICTION = 'Historical Fiction'
    HORROR = 'Horror'

    BIOGRAPHY_AUTOBIOGRAPHY = 'Biography/Autobiography'
    SELF_HELP = 'Self-Help'
    BUSINESS_FINANCE = 'Business/Finance'
    Non_Fiction_HISTORY = 'Non Fiction History'
    TRAVEL = 'Travel'
    HEALTH_FITNESS = 'Health/Fitness'
    COOKING_FOOD = 'Cooking/Food'
    RELIGION_SPIRITUALITY = 'Religion/Spirituality'
    SCIENCE_NATURE = 'Science/Nature'
    TECHNOLOGY_COMPUTERS = 'Technology/Computers'
    ART_PHOTOGRAPHY = 'Art/Photography'
    PHILOSOPHY = 'Philosophy'

    MATHEMATICS = 'Mathematics'
    PHYSICS = 'Physics'
    CHEMISTRY = 'Chemistry'
    BIOLOGY = 'Biology'
    LITERATURE = 'Literature'
    HISTORY = 'Academic History'
    PSYCHOLOGY = 'Psychology'
    SOCIOLOGY = 'Sociology'
    ECONOMICS = 'Economics'
    POLITICAL_SCIENCE = 'Political Science'
    LAW = 'Law'
    ENGINEERING = 'Engineering'
    MEDICINE = 'Medicine'
    COMPUTER_SCIENCE = 'Computer Science'

    PICTURE_BOOKS = 'Picture Books'
    EARLY_READERS = 'Early Readers'
    CHAPTER_BOOKS = 'Chapter Books'
    YOUNG_ADULT = 'Young Adult'

    POETRY = 'Poetry'
    SHORT_STORIES = 'Short Stories'
    ANTHOLOGIES = 'Anthologies'
    GRAPHIC_NOVELS_COMICS = 'Graphic Novels/Comics'
    REFERENCE_ENCYCLOPEDIAS = 'Reference/Encyclopedias'
    LANGUAGE_LEARNING = 'Language Learning'

class EBook(models.Model):
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length = 80, blank=False)
    summary = models.TextField(max_length=2000, blank=False)
    pages = models.CharField(max_length=80, null=True, blank=False)
    content = models.FileField(upload_to='ebooks/', blank=False)
    content_txt = models.TextField(null=True, blank=False)
    category = models.CharField(max_length=80, choices = Category.choices, blank=False)
    review_count = models.IntegerField(default=0)
    ratings = models.DecimalField(max_digits=3,decimal_places=2,default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateField(null=True, blank=False)
 
    def get_absolute_url(self):
        return f"ebook/{self.id}"
    
    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields=['author']), 
        ]
    
class Review(models.Model):
    ebook = models.ForeignKey(EBook, null=True, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(default=0)
    comment = models.TextField(max_length=1000, default="", blank=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ebook.title
        