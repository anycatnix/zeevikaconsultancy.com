"""
URL configuration for jobportal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from django.views.generic.base import TemplateView

from jobs.models import JobPost, Category
from blogs.models import Blog
from core.views import sitemap as custom_sitemap, robots_txt

# Sitemap configuration
sitemaps = {
    'jobs': GenericSitemap({
        'queryset': JobPost.objects.filter(is_active=True),
        'date_field': 'created_at',
    }, priority=0.8),
    'blogs': GenericSitemap({
        'queryset': Blog.objects.filter(is_published=True),
        'date_field': 'published_at',
    }, priority=0.6),
    'categories': GenericSitemap({
        'queryset': Category.objects.filter(is_active=True),
    }, priority=0.4),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('jobs.urls')),
    path('blogs/', include('blogs.urls')),
    path('contact/', include('contact.urls')),
    path('about/', include('core.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    # SEO URLs
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('robots.txt', robots_txt, name='robots_txt'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
