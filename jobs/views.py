from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator

from .models import JobPost, Category, Subcategory, FunctionalArea, State, City, CandidateApplication
from .forms import CandidateApplicationForm, JobSearchForm


def home(request):
    """Home page view with featured jobs and categories"""
    featured_jobs = JobPost.objects.filter(is_active=True, is_featured=True)[:6]
    latest_jobs = JobPost.objects.filter(is_active=True)[:20]
    categories = Category.objects.filter(is_active=True)[:8]

    # Fetch latest blogs from Blog model
    from blogs.models import Blog
    latest_blogs = Blog.objects.filter(is_published=True).order_by('-published_at')[:3]
    
    # Fetch featured companies
    from core.models import Company
    featured_companies = Company.objects.filter(is_active=True, is_featured=True)[:6]

    context = {
        'featured_jobs': featured_jobs,
        'latest_jobs': latest_jobs,
        'categories': categories,
        'search_form': JobSearchForm(),
        'latest_blogs': latest_blogs,
        'featured_companies': featured_companies,
    }
    return render(request, 'jobs/home.html', context)


class JobListView(ListView):
    model = JobPost
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 20

    def get_queryset(self):
        queryset = JobPost.objects.filter(is_active=True)
        
        # Apply search filters
        form = JobSearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data.get('keyword')
            location = form.cleaned_data.get('location')
            job_type = form.cleaned_data.get('job_type')
            experience_level = form.cleaned_data.get('experience_level')
            
            if keyword:
                queryset = queryset.filter(
                    Q(title__icontains=keyword) |
                    Q(company_name__icontains=keyword) |
                    Q(description__icontains=keyword) |
                    Q(skills__name__icontains=keyword)
                ).distinct()
            
            if location:
                queryset = queryset.filter(
                    Q(city__name__icontains=location) |
                    Q(state__name__icontains=location) |
                    Q(pin_code__icontains=location)
                )
            
            if job_type:
                queryset = queryset.filter(job_type=job_type)
            
            if experience_level:
                if experience_level == 'entry':
                    queryset = queryset.filter(experience_max__lte=2)
                elif experience_level == 'mid':
                    queryset = queryset.filter(experience_min__gte=3, experience_max__lte=5)
                elif experience_level == 'senior':
                    queryset = queryset.filter(experience_min__gte=6)
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = JobSearchForm(self.request.GET)
        context['categories'] = Category.objects.filter(is_active=True)
        context['job_types'] = JobPost.JOB_TYPE_CHOICES
        return context


class JobDetailView(DetailView):
    model = JobPost
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'

    def get_queryset(self):
        return JobPost.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.get_object()
        # Get related jobs
        related_jobs = JobPost.objects.filter(
            is_active=True,
            category=job.category
        ).exclude(id=job.id)[:4]
        context['related_jobs'] = related_jobs
        # Open Graph meta tags
        context['og_title'] = f"{job.title} at {job.company_name}"
        context['og_description'] = job.meta_description or job.description
        context['og_image'] = self.request.build_absolute_uri(job.company_logo.url) if job.company_logo else ''
        # Check if there are form errors in session
        if self.request.session.get('form_errors'):
            context['application_form'] = CandidateApplicationForm(data=self.request.session.get('form_data', {}))
            context['form_errors'] = self.request.session.get('form_errors')
            # Clear session data
            del self.request.session['form_errors']
            del self.request.session['form_data']
        else:
            context['application_form'] = CandidateApplicationForm()
        return context


@csrf_exempt
def apply_job(request, job_id):
    """Handle job application submission"""
    if request.method == 'POST':
        job = get_object_or_404(JobPost, id=job_id, is_active=True)
        form = CandidateApplicationForm(request.POST, request.FILES)
        
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            
            # Send email notification to admin
            try:
                subject = f'New Job Application: {job.title}'
                context = {
                    'application': application,
                    'job': job,
                }
                html_message = render_to_string('jobs/email/application_notification.html', context)
                plain_message = render_to_string('jobs/email/application_notification.txt', context)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.ADMIN_EMAIL] if hasattr(settings, 'ADMIN_EMAIL') else [settings.EMAIL_HOST_USER],
                    html_message=html_message,
                    fail_silently=True,  # Changed to True to prevent email errors from breaking the form
                )
            except Exception as e:
                # Log the error but don't fail the application
                print(f"Failed to send email notification: {e}")
            
            messages.success(request, 'Your application has been submitted successfully!')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Application submitted successfully!'
                })
            return redirect('jobs:job_detail', slug=job.slug)
        else:
            # Log form errors for debugging
            print(f"Form errors: {form.errors}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
            messages.error(request, 'Please correct the errors below.')
            # Return to job detail page with form errors
            return redirect('jobs:job_detail', slug=job.slug)
    
    return redirect('jobs:job_list')


def category_detail(request, slug):
    """Show jobs by category"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    jobs = JobPost.objects.filter(
        category=category, 
        is_active=True
    ).order_by('-created_at')
    
    # Get active categories with job counts
    categories = Category.objects.filter(
        is_active=True
    ).annotate(
        job_count=models.Count('jobs', filter=Q(jobs__is_active=True))
    ).order_by('name')
    
    paginator = Paginator(jobs, 10)  # Show 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'jobs': page_obj,
        'categories': categories,
        'search_form': JobSearchForm(),
    }
    return render(request, 'jobs/category_detail.html', context)


def subcategory_detail(request, slug):
    """Show jobs by subcategory"""
    subcategory = get_object_or_404(Subcategory, slug=slug, is_active=True)
    jobs = JobPost.objects.filter(subcategory=subcategory, is_active=True)
    
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'subcategory': subcategory,
        'jobs': page_obj,
        'search_form': JobSearchForm(),
    }
    return render(request, 'jobs/subcategory_detail.html', context)


def functional_area_detail(request, slug):
    """Show jobs by functional area"""
    functional_area = get_object_or_404(FunctionalArea, slug=slug, is_active=True)
    jobs = JobPost.objects.filter(functional_area=functional_area, is_active=True)
    
    paginator = Paginator(jobs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'functional_area': functional_area,
        'jobs': page_obj,
        'search_form': JobSearchForm(),
    }
    return render(request, 'jobs/functional_area_detail.html', context)


@method_decorator(staff_member_required, name='dispatch')
class ApplicationListView(ListView):
    model = CandidateApplication
    template_name = 'jobs/application_list.html'
    context_object_name = 'applications'
    paginate_by = 20

    def get_queryset(self):
        return CandidateApplication.objects.all().select_related('job')


@method_decorator(staff_member_required, name='dispatch')
class ApplicationDetailView(DetailView):
    model = CandidateApplication
    template_name = 'jobs/application_detail.html'
    context_object_name = 'application'


def load_cities(request):
    """AJAX view to load cities based on selected state"""
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id, is_active=True).order_by('name')
    return JsonResponse(list(cities.values('id', 'name')), safe=False)


def load_subcategories(request):
    """AJAX view to load subcategories based on selected category"""
    category_id = request.GET.get('category_id')
    subcategories = Subcategory.objects.filter(category_id=category_id, is_active=True).order_by('name')
    return JsonResponse(list(subcategories.values('id', 'name')), safe=False)


def load_functional_areas(request):
    """AJAX view to load functional areas based on selected subcategory"""
    subcategory_id = request.GET.get('subcategory_id')
    functional_areas = FunctionalArea.objects.filter(subcategory_id=subcategory_id, is_active=True).order_by('name')
    return JsonResponse(list(functional_areas.values('id', 'name')), safe=False)
