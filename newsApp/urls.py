from django.urls import path
from .views import *

urlpatterns = [
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryDetailView.as_view(), name='category-detail'),
    path('categories/<int:category_id>/articles/', ArticlesByCategoryView.as_view(), name='articles-by-category'),
    path('subcategories/', SubCategoryListCreateView.as_view(), name='subcategory-list'),
    path('subcategories/<int:pk>/', SubCategoryDetailView.as_view(), name='subcategory-detail'),
    path("categories/<int:category_id>/subcategories/", SubCategoriesByCategoryView.as_view(), name="subcategories-by-category"),
    path('subcategories/<int:subcategory_id>/articles/', ArticlesBySubCategoryView.as_view(), name='articles-by-subcategory'),
    path('articles/', ArticleListCreateView.as_view(), name='article-list'),
    path('articles/<int:pk>/', ArticleDetailView.as_view(), name='article-detail'),
    path('upload/', FileUploadView.as_view(), name='upload-file'),
    path('user/', UserAPIView.as_view(), name='create_user'),
]
