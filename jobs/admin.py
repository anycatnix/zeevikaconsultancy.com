from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Subcategory, FunctionalArea, State, City, JobPost, CandidateApplication


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'category__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category__name', 'name']


@admin.register(FunctionalArea)
class FunctionalAreaAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategory', 'category', 'slug', 'is_active', 'created_at']
    list_filter = ['subcategory__category', 'subcategory', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'subcategory__name', 'subcategory__category__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['subcategory__category__name', 'subcategory__name', 'name']

    def category(self, obj):
        return obj.subcategory.category.name
    category.short_description = 'Category'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'state', 'slug', 'is_active', 'created_at']
    list_filter = ['state', 'is_active', 'created_at']
    search_fields = ['name', 'state__name']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['state__name', 'name']


@admin.register(JobPost)
class JobPostAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'company_name', 'category', 'state', 'city', 
        'job_type', 'is_active', 'is_featured', 'created_at'
    ]
    list_filter = [
        'category', 'state', 'city', 'job_type', 'is_active', 
        'is_featured', 'created_at', 'expires_at'
    ]
    search_fields = [
        'title', 'company_name', 'description', 'category__name', 
        'state__name', 'city__name'
    ]
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'job_type', 'company_name', 'company_logo')
        }),
        ('Location', {
            'fields': ('state', 'city', 'pin_code')
        }),
        ('Category Information', {
            'fields': ('category', 'subcategory', 'functional_area')
        }),
        ('Job Details', {
            'fields': ('total_vacancy', 'salary_min', 'salary_max', 'salary_currency', 
                      'gender', 'experience_min', 'experience_max', 'skills', 'education', 'description')
        }),
        ('SEO Fields', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'classes': ('collapse',)
        }),
        ('Status and Dates', {
            'fields': ('is_active', 'is_featured', 'created_at', 'updated_at', 'expires_at')
        }),
    )
    ordering = ['-created_at']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'state', 'city')


@admin.register(CandidateApplication)
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'email', 'job', 'total_experience', 'status', 
        'applied_at', 'is_shortlisted', 'is_rejected'
    ]
    list_filter = [
        'job__category', 'job__state', 'is_shortlisted', 'is_rejected', 
        'applied_at', 'job__job_type'
    ]
    search_fields = [
        'name', 'email', 'job__title', 'job__company_name', 'message'
    ]
    readonly_fields = ['applied_at']
    fieldsets = (
        ('Application Information', {
            'fields': ('job', 'name', 'email', 'phone', 'total_experience', 'cv', 'message')
        }),
        ('Status', {
            'fields': ('is_shortlisted', 'is_rejected', 'admin_notes')
        }),
        ('Timestamps', {
            'fields': ('applied_at',),
            'classes': ('collapse',)
        }),
    )
    ordering = ['-applied_at']

    def status(self, obj):
        if obj.is_rejected:
            return format_html('<span style="color: red;">Rejected</span>')
        elif obj.is_shortlisted:
            return format_html('<span style="color: green;">Shortlisted</span>')
        return format_html('<span style="color: orange;">Pending</span>')
    status.short_description = 'Status'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('job')
