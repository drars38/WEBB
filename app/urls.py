from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf.urls.static import static
from posts import views
from rest_framework.routers import DefaultRouter
from posts.api import PostsViewset, TagViewset, CategoryViewset, AuthorViewset, CommentViewset, UserViewSet, UserProfileViewSet

router = DefaultRouter()
router.register('posts', PostsViewset, basename='posts')
router.register('tags', TagViewset, basename='tags')
router.register('authors', AuthorViewset, basename='authors')
router.register('categorys', CategoryViewset, basename='categorys')
router.register('comments', CommentViewset, basename='comments')
router.register(r'user', UserViewSet, basename='user')  # Регистрация UserViewSet
router.register(r'user-profile', UserProfileViewSet, basename='user-profile')  # Регистрация UserProfileViewSet
router.register(r'user/otp-status', UserProfileViewSet, basename='user-profile-otp-status')

urlpatterns = [
    path('posts/', views.ShowAllPostsTemplateView.as_view(), name='posts'),
    path('authors/', views.ShowAllAuthorsTemplateView.as_view(), name='authors'),
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
