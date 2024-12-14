from django.core.cache import cache

from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Avg, Max, Min
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, viewsets, status
from rest_framework import serializers
from posts.models import Post, Tag, Comment, Category, Author
from posts.serializers import PostSerializer, TagSerializer, CommentSerializer, CategorySerializer, AuthorSerializer
import pyotp
import logging



class TagViewset(mixins.CreateModelMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 mixins.UpdateModelMixin,
                 mixins.DestroyModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def stats(self, request, *args, **kwargs):
        stats = Tag.objects.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)

        return Response(serializer.data)


class CategoryViewset(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.UpdateModelMixin,
                      mixins.DestroyModelMixin,
                      GenericViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class PostsViewset(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   GenericViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.is_authenticated:
            return queryset.none()  # Возвращаем пустой QuerySet для анонимных пользователей

        # Фильтрация по автору для обычных пользователей
        if not self.request.user.is_superuser:
            authors = Author.objects.filter(user=self.request.user)
            queryset = queryset.filter(author__in=authors)

        # Фильтрация по категориям
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__id=category)

        # Фильтрация по тегам
        tags = self.request.query_params.getlist('tags')  # Получаем список тегов
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()  # Применяем фильтрацию по тегам и используем distinct для удаления дублирующихся постов

        # Фильтрация по автору (если есть)
        author = self.request.query_params.get('author')
        if author:
            queryset = queryset.filter(author__id=author)

        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a post.")

        # Получаем первого автора для текущего пользователя
        author = Author.objects.filter(user=self.request.user).first()
        if not author:
            raise PermissionDenied("No author associated with this user.")

        serializer.save(author=author)

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def stats(self, request, *args, **kwargs):
        stats = Post.objects.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)

        return Response(serializer.data)



from rest_framework.exceptions import ValidationError


class CommentViewset(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        if not self.request.user.is_superuser:
            # Получаем всех авторов, связанных с текущим пользователем
            authors = Author.objects.filter(user=self.request.user)
            if authors.exists():
                queryset = queryset.filter(author__in=authors)  # Фильтрация по авторам пользователя
            else:
                return queryset.none()

        return queryset

    def perform_create(self, serializer):
        # Получаем всех авторов текущего пользователя
        authors = Author.objects.filter(user=self.request.user)

        if not authors.exists():
            raise ValidationError("No authors associated with this user.")

        # Выводим данные запроса, чтобы проверить, что приходит
        print("Request data:", self.request.data)

        # Проверяем, передан ли автор в запросе
        requested_author_id = self.request.data.get('author')  # Получаем ID автора из данных запроса
        print(f"Requested author ID: {requested_author_id}")  # Логирование ID автора

        if not requested_author_id:
            raise ValidationError("Author ID must be provided.")

        # Ищем автора среди авторов текущего пользователя
        requested_author = authors.filter(id=requested_author_id).first()

        if requested_author:
            # Дополнительно проверяем, что найденный автор принадлежит текущему пользователю
            if requested_author.user.id != self.request.user.id:
                raise ValidationError("The specified author does not belong to the current user.")
            print(f"Found author ID: {requested_author.id}, Bio: {requested_author.bio}")  # Логирование ID и bio автора
        else:
            print("No author found matching the requested ID.")

        if not requested_author:
            raise ValidationError("The specified author does not belong to the current user.")

        # Сохраняем комментарий, привязывая его к выбранному автору
        serializer.save(author=requested_author)



class AuthorViewset(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    GenericViewSet):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            # Возвращаем пустой QuerySet для анонимного пользователя
            return Author.objects.none()

        queryset = Author.objects.all()
        if not self.request.user.is_superuser:
            # Фильтруем авторов только текущего пользователя
            queryset = queryset.filter(user=self.request.user)
        return queryset

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def reset_otp(self, request, *args, **kwargs):
        author = request.user.author_user
        author.otp_key = pyotp.random_base32()
        author.save()
        return Response({'success': True, 'new_otp_key': author.otp_key})

    class StatsSerializer(serializers.Serializer):
        count = serializers.IntegerField()
        avg = serializers.FloatField()
        max = serializers.IntegerField()
        min = serializers.IntegerField()

    @action(detail=False, methods=['GET'], url_path='stats')
    def stats(self, request, *args, **kwargs):
        stats = Author.objects.aggregate(
            count=Count('*'),
            avg=Avg('id'),
            max=Max('id'),
            min=Min('id'),
        )

        serializer = self.StatsSerializer(instance=stats)

        return Response(serializer.data)


class EmptySerializer(serializers.Serializer):
    pass


from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
import pyotp
from django.contrib.auth import authenticate, login
import logging

class UserViewSet(GenericViewSet):
    serializer_class = EmptySerializer

    # Метод для логина
    @action(url_path='login', methods=['POST'], detail=False)
    def login_(self, request):
        username = request.data.get('username')
        password = request.data.get('password')  # Получаем пароль

        # Проверка на обязательные поля
        if not username or not password:
            return Response(
                {'error': 'Имя пользователя и пароль обязательны.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)

        if user:
            # Генерация OTP-ключа, если его еще нет
            if not user.otp_key:
                otp = pyotp.random_base32()  # Генерация OTP ключа
                user.otp_key = otp
                user.save()

                # Вывод OTP в консоль, если он был сгенерирован
                print(f"OTP key generated for user {username}: {otp}")
            else:
                login(request, user)
                print(f"User {username} already has OTP key: {user.otp_key}")

            # Создаем объект TOTP с использованием OTP секрета
            totp = pyotp.TOTP(user.otp_key, interval=30)  # Устанавливаем интервал действия OTP в 30 секунд

            # Генерируем текущий OTP код для пользователя
            generated_otp = totp.now()

            # Печатаем OTP код, который генерируется для пользователя
            print(f"Generated OTP code for user {username}: {generated_otp}")

            # Если у пользователя есть OTP-ключ, требуется двухфакторная аутентификация
            return Response({
                'otp_required': True,
                'success': 'OTP требуется',
                'otp_key': user.otp_key,  # Отправляем OTP ключ на случай, если нужно
                'generated_otp': generated_otp  # Отправляем OTP код (для тестов или отладки)
            })

        else:
            return Response(
                {'error': 'Неверное имя пользователя или пароль.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

    # Метод для верификации OTP
    @action(detail=False, url_path='otp-login', methods=['POST'])
    def otp_login(self, request, *args, **kwargs):
        # Проверяем, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован.'}, status=status.HTTP_401_UNAUTHORIZED)

        otp_code = request.data.get('otp_code')  # Получаем OTP из запроса
        if not otp_code:
            return Response({'error': 'OTP код обязателен.'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if not user.otp_key:
            return Response({'error': 'OTP ключ не найден.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(user.otp_key, interval=30)  # Устанавливаем интервал действия OTP в 30 секунд
        if totp.verify(otp_code):  # Проверяем введенный OTP код
            # Успешная верификация OTP
            print(f"OTP code {otp_code} verified successfully for user {user.username}")  # Выводим успешную верификацию
            login(request, user)  # Выполняем вход после успешной верификации OTP

            # Сохраняем информацию о подтвержденном OTP в кэш
            cache.set(f'otp_good_{user.id}', True, timeout=3600)  # timeout можно настроить по вашему усмотрению

            return Response({'success': 'OTP верифицирован успешно.'})
        else:
            print(
                f"OTP verification failed for user {user.username} with code {otp_code}")  # Выводим неудачную верификацию
            return Response({'error': 'Неверный OTP код.'}, status=status.HTTP_400_BAD_REQUEST)

    # Метод для получения информации о пользователе
    @action(url_path='info', methods=['GET'], detail=False)
    def info(self, request):
        # Проверка аутентификации
        if not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Проверка, прошел ли пользователь верификацию OTP
        otp_verified = cache.get(f'otp_good_{request.user.id}', False)
        print(f"OTP Verified: {otp_verified}")  # Для отладки, выводим состояние флага

        if not otp_verified:
            logout(request)
            # Если OTP не подтвержден, возвращаем флаги otpVerified и otpRequired
            return Response({
                'error': 'OTP не подтвержден. Доступ к информации ограничен.',
                'otpVerified': False,
                'otpRequired': True
            }, status=status.HTTP_403_FORBIDDEN)

        # Если OTP верифицирован, возвращаем информацию о пользователе
        data = {
            'is_authenticated': request.user.is_authenticated,
            'username': request.user.username,
            'user_id': request.user.id,
            'is_superuser': request.user.is_superuser,
            'otpVerified': True,  # OTP верифицирован
            'otpRequired': False  # OTP больше не требуется
        }
        return Response(data)

    # Метод для проверки состояния OTP
    @action(detail=False, url_path='otp-status', methods=['GET'])
    def otp_status(self, request):
        # Проверяем, что пользователь аутентифицирован
        if not request.user.is_authenticated:
            return Response({'error': 'Пользователь не аутентифицирован.'}, status=status.HTTP_401_UNAUTHORIZED)

        # Проверяем, подтвержден ли OTP для пользователя
        otp_verified = cache.get(f'otp_good_{request.user.id}', False)

        # Возвращаем статус подтверждения OTP
        return Response({'otp_verified': otp_verified})

    # Метод для выхода из аккаунта
    @action(detail=False, url_path='logout', methods=['POST'])
    def logout_(self, request):
        if request.user.is_authenticated:
            logout(request)
            return Response({'success': 'Вы успешно вышли из системы.'})
        return Response({'error': 'Пользователь не аутентифицирован.'}, status=status.HTTP_401_UNAUTHORIZED)




class UserProfileViewSet(GenericViewSet):
    permission_classes = [IsAuthenticated]

    class OTPSerializer(serializers.Serializer):
        key = serializers.CharField()

    class OTPRequired(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and cache.get('otp_good', False))

    @action(detail=False, url_path="check-login", methods=['GET'], permission_classes=[])
    def get_check_login(self, request, *args, **kwargs):
        return Response({
            'is_authenticated': self.request.user.is_authenticated
        })

    @action(detail=False, url_path="login", methods=['POST'], permission_classes=[])
    def use_login(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            try:
                author = user.author_user
            except AttributeError:
                return Response({'error': 'Нет привязанного автора.'}, status=status.HTTP_400_BAD_REQUEST)

            # Генерируем OTP
            totp = pyotp.TOTP(author.otp_key)
            otp_code = totp.now()

            # Здесь вы должны отправить `otp_code` пользователю через безопасный канал
            logging.info(f"Ваш OTP код: {otp_code}")

            return Response({'requires_otp': True})

        return Response({'error': 'Неверные учетные данные.'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, url_path='otp-login', methods=['POST'], serializer_class=OTPSerializer)
    def otp_login(self, request, *args, **kwargs):
        try:
            author = request.user.author_user
        except AttributeError:
            return Response({'error': 'Автор не найден.'}, status=status.HTTP_400_BAD_REQUEST)

        totp = pyotp.TOTP(author.otp_key)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        success = totp.verify(serializer.validated_data['key'])
        if success:
            cache.set(f'otp_good_{request.user.id}', True, timeout=36000)  # Кэшируем подтверждение на 10 минут
        else:
            return Response({'error': 'Неверный OTP код.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'success': success})

    @action(detail=False, url_path='otp-status', methods=['GET'])
    def get_otp_status(self, request, *args, **kwargs):
        otp_good = cache.get(f'otp_good_{request.user.id}', False)
        return Response({'otp_good': otp_good})

    @action(detail=False, url_path='otp-required', permission_classes=[OTPRequired], methods=['GET'])
    def page_with_otp_required(self, request, *args, **kwargs):
        return Response({
            'success': True
        })
