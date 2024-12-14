from rest_framework import serializers
from .models import Post, Author, Category, Tag, Comment

import pyotp

class AuthorSerializer(serializers.ModelSerializer):
    otp_key = serializers.CharField(read_only=True)  # Чтобы не позволять напрямую изменять OTP-ключ

    def create(self, validated_data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is required.")

        # Связываем пользователя с автором
        validated_data['user'] = request.user

        # Генерируем OTP-ключ, если он не задан
        validated_data['otp_key'] = pyotp.random_base32()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Обновление ключа OTP, если пользователь запросил его смену
        if 'reset_otp' in self.context:  # Передаем `reset_otp` через контекст
            instance.otp_key = pyotp.random_base32()
        return super().update(instance, validated_data)

    class Meta:
        model = Author
        fields = ['id', 'bio', 'picture', 'user', 'otp_key']
        read_only_fields = ['user', 'otp_key']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']

class PostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    tags = serializers.PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'category', 'tags', 'picture']

class CommentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'post', 'author']




    def validate(self, data):
        # Защита от передачи поля author вручную
        if 'author' in data:
            raise serializers.ValidationError("You cannot manually specify the author.")
        return data

    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'post']
        read_only_fields = ['author']
