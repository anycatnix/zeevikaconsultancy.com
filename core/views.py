from django.shortcuts import render
from django.views.generic import TemplateView
from jobs.models import JobPost, Category
from blogs.models import Blog
from core.models import Testimonial, Company
from jobs.forms import JobSearchForm


class AboutView(TemplateView):
    template_name = 'core/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm()
        context['testimonials'] = Testimonial.objects.filter(is_active=True)[:6]
        context['featured_companies'] = Company.objects.filter(is_featured=True, is_active=True)[:8]
        context['total_jobs'] = JobPost.objects.filter(is_active=True).count()
        context['total_categories'] = Category.objects.filter(is_active=True).count()
        return context


def sitemap(request):
    """Generate sitemap for SEO"""
    jobs = JobPost.objects.filter(is_active=True)
    blogs = Blog.objects.filter(is_published=True)
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'jobs': jobs,
        'blogs': blogs,
        'categories': categories,
    }
    return render(request, 'core/sitemap.xml', context, content_type='application/xml')


def robots_txt(request):
    """Generate robots.txt for SEO"""
    return render(request, 'core/robots.txt', content_type='text/plain')
