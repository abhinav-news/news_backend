from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/', CategoryDetailView.as_view(), name='category-detail'),

    path('subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list'),
    path('subcategories/<uuid:pk>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),
    path("categories/<uuid:category_id>/subcategories/", SubCategoriesByCategoryView.as_view(), name="subcategories-by-category"),

    path('articles/', ArticleListCreateView.as_view(), name='article-list'),
    path('articles/<uuid:pk>/', ArticleDetailView.as_view(), name='article-detail'),

    path('upload/', FileUploadView.as_view(), name='upload-file'),
    path('user/', UserAPIView.as_view(), name='create_user'),
]
