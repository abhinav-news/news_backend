from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, SubCategory, Article
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubCategorySerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = SubCategory
        fields = ['id', 'category', 'category_name', 'name', 'slug', 'created_at', 'updated_at']


class ArticleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    subcategory_name = serializers.CharField(source='subcategory.name', read_only=True)
    title = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=Article.objects.all())]
    )

    class Meta:
        model = Article
        fields = [
            'id', 'title', 'slug', 'author',
            'category', 'category_name',
            'subcategory', 'subcategory_name',
            'summary', 'content', 'banner_image',
            'is_published', 'published_at', 'tag',
            'created_at', 'updated_at'
        ]

class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    is_staff = serializers.BooleanField(default=False)
    is_superuser = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password', 'is_staff', 'is_superuser', 'is_active')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.username = validated_data.get('email') or user.email
        user.set_password(password)
        user.save()
        return user
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance