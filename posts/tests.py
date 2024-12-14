from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from model_bakery import baker
from posts.models import Post, Tag, Author, Category
from django.contrib.auth.models import User


class PostsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создание пользователя, который связан с автором
        self.user = User.objects.create_user(username="testuser", password="testpassword")

        # Создание автора
        self.author = Author.objects.create(user=self.user, bio='Автор тестов')

        # Создание категории
        self.category = Category.objects.create(name='Категория тестов')

        # Создание тега
        self.tag = Tag.objects.create(name='Тег тестов')

        # Создание поста
        self.post = Post.objects.create(
            author=self.author,
            category=self.category,
            title='Тестовый пост',
            content='Тестовое содержание',
        )
        self.post.tags.add(self.tag)

    def test_get_list(self):
        response = self.client.get('/api/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        post_data = data[0]

        # Проверка данных поста
        self.assertEqual(post_data['title'], self.post.title)
        self.assertEqual(post_data['content'], self.post.content)

        # Проверка данных автора
        self.assertEqual(post_data['author']['bio'], self.author.bio)

        # Проверка данных категории
        self.assertEqual(post_data['category']['name'], self.category.name)

        # Проверка данных тегов
        self.assertEqual(post_data['tags'][0]['name'], self.tag.name)





class PostCreateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создание необходимых объектов
        self.author = baker.make('posts.Author')
        self.category = baker.make('posts.Category')
        self.tag = baker.make('posts.Tag')

        # Формирование данных для создания поста
        self.post_data = {
            'title': 'Тестовый пост',
            'content': 'Тестовое содержание',
            'author': self.author.id,
            'category': self.category.id,
            'tags': [self.tag.id]
        }

    def test_create_post(self):
        response = self.client.post('/api/posts/', self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Дополнительные проверки
        response_data = response.json()
        self.assertEqual(response_data['title'], self.post_data['title'])
        self.assertEqual(response_data['content'], self.post_data['content'])
        self.assertEqual(response_data['author'], self.post_data['author'])
        self.assertEqual(response_data['category'], self.post_data['category'])
        self.assertIn(self.tag.id, response_data['tags'])




class PostDeleteTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создание объектов с помощью model_bakery
        self.author = baker.make('posts.Author')
        self.category = baker.make('posts.Category')
        self.tag = baker.make('posts.Tag')

        # Создание поста
        self.post = baker.make('posts.Post', author=self.author, category=self.category, tags=[self.tag])

    def test_delete_post(self):
        # Проверяем, что пост существует перед удалением
        response = self.client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Отправляем запрос на удаление
        response = self.client.delete(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Проверяем, что пост больше не существует
        response = self.client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)




class PostUpdateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Создание объектов с помощью model_bakery
        self.author = baker.make('posts.Author')
        self.category = baker.make('posts.Category')
        self.tag = baker.make('posts.Tag')

        # Создание поста
        self.post = baker.make('posts.Post', author=self.author, category=self.category, tags=[self.tag])

        # Данные для обновления
        self.update_data = {
            'title': 'Updated Title',
            'content': 'Updated Content',
            'author': self.author.id,
            'category': self.category.id,
            'tags': [self.tag.id]
        }

    def test_update_post(self):
        # Проверяем, что объект существует перед обновлением
        response = self.client.get(f'/api/posts/{self.post.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Отправляем запрос на обновление
        response = self.client.put(f'/api/posts/{self.post.id}/', self.update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверяем, что данные обновлены
        updated_post = response.json()
        self.assertEqual(updated_post['title'], self.update_data['title'])
        self.assertEqual(updated_post['content'], self.update_data['content'])
        self.assertEqual(updated_post['author'], self.update_data['author'])
        self.assertEqual(updated_post['category'], self.update_data['category'])
        self.assertEqual(updated_post['tags'], self.update_data['tags'])

        # Дополнительно, проверяем, что старые данные не присутствуют
        old_post_response = self.client.get(f'/api/posts/{self.post.id}/')
        old_post_data = old_post_response.json()
        self.assertNotEqual(old_post_data['title'], 'Тестовый пост')
        self.assertNotEqual(old_post_data['content'], 'Тестовое содержание')
