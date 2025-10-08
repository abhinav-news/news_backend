import os
import boto3
import uuid
from rest_framework import generics, status, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Category, Article
from .permissions import IsAdminOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from .serializers import *
from .pagination import StandardResultsSetPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings



# CATEGORY VIEWS
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all().order_by('-updated_at')
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['updated_at', 'created_at', 'name']
    ordering = ['-updated_at']

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]


# ARTICLE VIEWS
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all().order_by('-updated_at')
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_published', 'tag' , 'slug']
    search_fields = ['title', 'summary', 'slug']
    ordering_fields = ['updated_at', 'created_at', 'title']
    ordering = ['-updated_at']
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        related_kw = self.request.query_params.get('related_keywords')
        if related_kw:
            queryset = queryset.filter(related_keywords__icontains=related_kw)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)

        counts = {
            'published': queryset.filter(is_published=True).count(),
            'draft': queryset.filter(is_published=False).count(),
        }

        # Pass counts to pagination response
        return self.paginator.get_paginated_response(serializer.data, counts=counts)

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]


# ARTICLES BY CATEGORY
class ArticlesByCategoryView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        category_id = self.kwargs['category_id']
        return Article.objects.filter(category_id=category_id).order_by('-updated_at')


class FileUploadView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']
            
            # Generate unique filename
            ext = os.path.splitext(file.name)[1]
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            
            try:
                # METHOD 1: Use boto3 directly (recommended for debugging)
                session = boto3.session.Session()
                s3_client = session.client(
                    's3',
                    region_name=settings.AWS_S3_REGION_NAME,
                    endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                
                # Upload file using boto3 directly
                s3_client.upload_fileobj(
                    file.file,  # Use file.file for UploadedFile object
                    settings.AWS_STORAGE_BUCKET_NAME,
                    unique_filename,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': file.content_type or 'application/octet-stream'
                    }
                )
                
                # Construct URL
                endpoint_url = settings.AWS_S3_ENDPOINT_URL.rstrip('/')
                file_url = f"{endpoint_url}/{settings.AWS_STORAGE_BUCKET_NAME}/{unique_filename}"
                
                # Verify upload
                try:
                    s3_client.head_object(
                        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                        Key=unique_filename
                    )
                    print("File successfully verified in DigitalOcean Spaces")
                except Exception as e:
                    print(f"File verification failed: {e}")
                    return Response(
                        {"error": "File upload verification failed"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )
                
                return Response({
                    "url": file_url,
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                print(f"Upload error: {str(e)}")
                return Response(
                    {"error": f"Upload failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserAPIView(APIView):
    def get_permissions(self):
        # POST is public, PATCH requires authentication
        if self.request.method == "POST":
            return [AllowAny()]
        return [IsAuthenticated()]

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
            except Exception as e:
                return Response(
                    {"error": f"User creation failed: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "message": "User created successfully",
                "user_id": user.id,
                "email": user.email
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        # Partial update of logged-in user
        user = request.user
        serializer = UserCreateSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    user = serializer.save()
            except Exception as e:
                return Response(
                    {"error": f"User update failed: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "message": "User updated successfully"
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)