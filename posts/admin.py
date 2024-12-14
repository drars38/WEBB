from django.contrib import admin
from .models import Author, Category, Tag, Post, Comment

# Регистрация модели Author
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'bio')
    search_fields = ('user__username', 'bio')

# Регистрация моделей в админке
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Укажите поля для отображения в списке
    search_fields = ('name',)      # Поле для поиска
    ordering = ('id',)             # Сортировка


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'category')
    search_fields = ('title', 'content', 'author__user__username')  # Поиск по автору
    list_filter = ('category', 'tags', 'author')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'author', 'created_at')
    search_fields = ('content', 'author__user__username')  # Поиск по автору комментария
    list_filter = ('post', 'author', 'created_at')
