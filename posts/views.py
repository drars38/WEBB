from django.views.generic import TemplateView

from django.http import HttpResponse
import qrcode
import io
from .models import Author, Post, Tag


# HTML-представление дл€ авторов
class ShowAllAuthorsTemplateView(TemplateView):
    template_name = "posts/show_authors.html"  # ”бедитесь, что у вас есть такой шаблон

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ѕровер€ем анонимного пользовател€ и возвращаем пустой список
        if self.request.user.is_anonymous:
            context['authors'] = []
            return context

        # ≈сли суперпользователь, возвращаем всех авторов, иначе фильтруем по текущему пользователю
        context['authors'] = Author.objects.all() if self.request.user.is_superuser else Author.objects.filter(
            user=self.request.user)
        return context


# HTML-представление дл€ постов
class ShowAllPostsTemplateView(TemplateView):
    template_name = "posts/show_posts.html"  # ”бедитесь, что у вас есть такой шаблон

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ѕровер€ем анонимного пользовател€ и возвращаем пустой список
        if self.request.user.is_anonymous:
            context['posts'] = []
            return context

        # ≈сли суперпользователь, возвращаем все посты, иначе фильтруем по автору пользовател€
        author = Author.objects.filter(user=self.request.user).first()
        context['posts'] = Post.objects.all() if self.request.user.is_superuser else Post.objects.filter(author=author)
        return context


# HTML-представление дл€ тэгов
class ShowAllTagsTemplateView(TemplateView):
    template_name = "posts/show_tags.html"  # ”бедитесь, что у вас есть такой шаблон

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ѕровер€ем анонимного пользовател€ и возвращаем пустой список
        if self.request.user.is_anonymous:
            context['tags'] = []
            return context

        # ≈сли суперпользователь, возвращаем все теги, иначе фильтруем по каким-либо услови€м, если это требуетс€
        context['tags'] = Tag.objects.all()
        return context


