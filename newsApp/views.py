from rest_framework import generics, permissions, status
from .models import Category, SubCategory, Article
from .serializers import CategorySerializer, SubCategorySerializer, ArticleSerializer, FileUploadSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.files.storage import default_storage
from django.conf import settings
import os
import boto3
import uuid

# Permissions
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_staff

# CATEGORY VIEWS
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

# SUBCATEGORY VIEWS
class SubCategoryListCreateView(generics.ListCreateAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAdminOrReadOnly]

class SubCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategorySerializer
    permission_classes = [IsAdminOrReadOnly]

# ARTICLE VIEWS
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]

class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminOrReadOnly]


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
