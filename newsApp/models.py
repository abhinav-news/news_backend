from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from uuid import uuid4


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or "Unnamed Category"


class SubCategory(BaseModel):
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True, null=True, blank=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.name and self.category:
            return f"{self.category.name} - {self.name}"
        return self.name or "Unnamed Subcategory"


class Article(BaseModel):

    class TagChoices(models.TextChoices):
        BREAKING_NEWS = 'breaking_news', 'Breaking News'
        TRENDING_NOW = 'trending_now', 'Trending Now'
        FEATURED = 'featured', 'Featured'
        EXCLUSIVE = 'exclusive', 'Exclusive'
        ADVERTISEMENT = 'advertisement', 'Advertisement'
        HAPPENING_NOW = 'happening_now', 'Happening Now'

    title = models.CharField(max_length=255, unique=True, null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True, max_length=255)
    author = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    banner_image = models.CharField(max_length=600, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    tag = models.CharField(max_length=100, choices=TagChoices.choices, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug and self.title:
            self.slug = slugify(self.title)
        if self.is_published and not self.published_at:
            from django.utils.timezone import now
            self.published_at = now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title or "Untitled Article"
