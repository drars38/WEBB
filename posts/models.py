import pyotp
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser

from app import settings


class CustomUser(AbstractUser):
    otp_key = models.CharField('OTP Key', max_length=32, blank=True, null=True)

# Модель Автор
class Author(models.Model):
    bio = models.TextField(blank=True, null=True)
    picture = models.ImageField("Изображение", null=True, upload_to="authors")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, verbose_name="Пользователь", related_name='author_user')


    def __str__(self):
        return self.user.username



# Категория
class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Теги
class Tag(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Статья
class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Связь с моделью Author
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag)
    picture = models.ImageField("Изображение", null=True, upload_to="posts")

    def __str__(self):
        return self.title

# Комментарий
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='commentss')
    author = models.ForeignKey(Author, on_delete=models.CASCADE)  # Связь с моделью Author
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author} on {self.post.title}"
