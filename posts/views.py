from django.views.generic import TemplateView

from django.http import HttpResponse
import qrcode
import io
from .models import Author, Post, Tag


# HTML-������������� ��� �������
class ShowAllAuthorsTemplateView(TemplateView):
    template_name = "posts/show_authors.html"  # ���������, ��� � ��� ���� ����� ������

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ��������� ���������� ������������ � ���������� ������ ������
        if self.request.user.is_anonymous:
            context['authors'] = []
            return context

        # ���� �����������������, ���������� ���� �������, ����� ��������� �� �������� ������������
        context['authors'] = Author.objects.all() if self.request.user.is_superuser else Author.objects.filter(
            user=self.request.user)
        return context


# HTML-������������� ��� ������
class ShowAllPostsTemplateView(TemplateView):
    template_name = "posts/show_posts.html"  # ���������, ��� � ��� ���� ����� ������

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ��������� ���������� ������������ � ���������� ������ ������
        if self.request.user.is_anonymous:
            context['posts'] = []
            return context

        # ���� �����������������, ���������� ��� �����, ����� ��������� �� ������ ������������
        author = Author.objects.filter(user=self.request.user).first()
        context['posts'] = Post.objects.all() if self.request.user.is_superuser else Post.objects.filter(author=author)
        return context


# HTML-������������� ��� �����
class ShowAllTagsTemplateView(TemplateView):
    template_name = "posts/show_tags.html"  # ���������, ��� � ��� ���� ����� ������

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ��������� ���������� ������������ � ���������� ������ ������
        if self.request.user.is_anonymous:
            context['tags'] = []
            return context

        # ���� �����������������, ���������� ��� ����, ����� ��������� �� �����-���� ��������, ���� ��� ���������
        context['tags'] = Tag.objects.all()
        return context


