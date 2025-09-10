from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'is_published', 'is_featured', 'published_at', 'created_at'
    ]
    list_filter = ['is_published', 'is_featured', 'published_at', 'created_at']
    search_fields = ['title', 'description', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    filter_horizontal = ['tags']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'description', 'content', 'image')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Tags and Categories', {
            'fields': ('tags',),
            'classes': ('collapse',)
        }),
        ('Status and Dates', {
            'fields': ('is_published', 'is_featured', 'created_at', 'updated_at', 'published_at')
        }),
    )
    ordering = ['-published_at']
