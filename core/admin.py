from django.contrib import admin
from .models import Company, Testimonial, SiteSettings


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'is_featured', 'is_active', 'created_at'
    ]
    list_filter = ['is_featured', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'position', 'company', 'rating', 'is_active', 'created_at'
    ]
    list_filter = ['rating', 'is_active', 'created_at']
    search_fields = ['name', 'position', 'company', 'content']
    ordering = ['-created_at']


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion
        return False
