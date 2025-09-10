from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.generic import ListView, DetailView
from .models import Blog
from jobs.forms import JobSearchForm


class BlogListView(ListView):
    model = Blog
    template_name = 'blogs/blog_list.html'
    context_object_name = 'blogs'
    paginate_by = 10

    def get_queryset(self):
        queryset = Blog.objects.filter(is_published=True)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm()
        context['featured_blogs'] = Blog.objects.filter(is_published=True, is_featured=True)[:3]
        return context


class BlogDetailView(DetailView):
    model = Blog
    template_name = 'blogs/blog_detail.html'
    context_object_name = 'blog'

    def get_queryset(self):
        return Blog.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        blog = self.get_object()
        # Get related blogs
        related_blogs = Blog.objects.filter(
            is_published=True,
            tags__in=blog.tags.all()
        ).exclude(id=blog.id)[:3]
        context['related_blogs'] = related_blogs
        context['search_form'] = JobSearchForm()
        # Open Graph meta tags
        context['og_title'] = blog.title
        context['og_description'] = blog.meta_description or blog.description
        context['og_image'] = self.request.build_absolute_uri(blog.image.url) if blog.image else ''
        return context


def blog_search(request):
    """Search blogs by keyword"""
    query = request.GET.get('q', '')
    blogs = []
    
    if query:
        blogs = Blog.objects.filter(
            is_published=True
        ).filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    paginator = Paginator(blogs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'blogs': page_obj,
        'query': query,
        'search_form': JobSearchForm(),
    }
    return render(request, 'blogs/blog_search.html', context)
