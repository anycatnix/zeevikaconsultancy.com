from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    content = RichTextField()
    image = models.ImageField(upload_to='blogs/', blank=True, null=True)
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Tags and Categories
    tags = TaggableManager(blank=True)
    
    # Status and Dates
    is_published = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(auto_now_add=True)
    
    # History
    history = HistoricalRecords()

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.description[:160] if self.description else ""
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blogs:blog_detail', kwargs={'slug': self.slug})

    @property
    def excerpt(self):
        """Return first 150 characters of description"""
        return self.description[:150] + "..." if len(self.description) > 150 else self.description
