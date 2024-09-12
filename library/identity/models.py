from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

# Create your models here.
class Roles(models.TextChoices):
    ADMIN = 'Admin'
    GUEST = 'Guest'
    READER = 'Reader'
    WRITER = 'Writer'

class Role(models.Model):
    name = models.CharField(max_length=10, choices=Roles.choices)
    
class Gender(models.TextChoices):
    MALE = 'Male'
    FEMALE = 'Female'


class UserManager(BaseUserManager):
    def create_user(self, first_name, last_name, username, date_of_birth, gender, password=None):
        """
        Creates and saves a User with the given username, date of
        birth and password.
        """
        if not username:
            raise ValueError("Users must have an email address")

        user = self.model(
            first_name=first_name,
            last_name=last_name,
            username=self.normalize_email(username),
            date_of_birth=date_of_birth,
            gender=gender,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, first_name, last_name, username, date_of_birth, gender, password=None):
        """
        Creates and saves a superuser with the given username, date of
        birth and password.
        """
        user = self.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            password=password,
            date_of_birth=date_of_birth,
            gender=gender,
        )
        user.is_admin = True
        user.save(using=self._db)
        admin_role, created = Role.objects.get_or_create(name=Roles.ADMIN)
        user.roles.add(admin_role)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(max_length=30, null=True, blank=False)
    last_name = models.CharField(max_length=30, null=True,blank=False)
    username = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=False)
    roles = models.ManyToManyField(Role, related_name='users', blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["date_of_birth","first_name","last_name","gender"]

    def get_absolute_url(self):
        return f"users/{self.id}"
    
    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin
    
    def get_full_name(self):
        "Returns the user's full name."
        return f"{self.first_name} {self.last_name}".strip()
    
class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile',on_delete=models.CASCADE)
    one_time_password = models.CharField(max_length=50, default="", blank=True)
    one_time_password_expire = models.DateTimeField(null=True, blank=True)
