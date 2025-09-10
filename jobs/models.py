from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from taggit.managers import TaggableManager
from ckeditor.fields import RichTextField
from simple_history.models import HistoricalRecords


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:category_detail', kwargs={'slug': self.slug})


class Subcategory(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Subcategories"
        ordering = ['name']
        unique_together = ['category', 'name']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.category.name}-{self.name}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:subcategory_detail', kwargs={'slug': self.slug})


class FunctionalArea(models.Model):
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='functional_areas')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Functional Areas"
        ordering = ['name']
        unique_together = ['subcategory', 'name']

    def __str__(self):
        return f"{self.subcategory.category.name} - {self.subcategory.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.subcategory.category.name}-{self.subcategory.name}-{self.name}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:functional_area_detail', kwargs={'slug': self.slug})


class State(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Cities"
        ordering = ['name']
        unique_together = ['state', 'name']

    def __str__(self):
        return f"{self.state.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.state.name}-{self.name}")
        super().save(*args, **kwargs)


class JobPost(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('freelance', 'Freelance'),
        ('internship', 'Internship'),
    ]

    GENDER_CHOICES = [
        ('any', 'Any'),
        ('male', 'Male'),
        ('female', 'Female'),
    ]

    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    
    # Company Information
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Location Information
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='jobs')
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='jobs')
    pin_code = models.CharField(max_length=10, blank=True)
    
    # Category Information
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='jobs')
    subcategory = models.ForeignKey(Subcategory, on_delete=models.CASCADE, related_name='jobs')
    functional_area = models.ForeignKey(FunctionalArea, on_delete=models.CASCADE, related_name='jobs')
    
    # Job Details
    total_vacancy = models.PositiveIntegerField(default=1)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='USD')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='any')
    experience_min = models.PositiveIntegerField(blank=True, null=True, help_text="Years of experience")
    experience_max = models.PositiveIntegerField(blank=True, null=True, help_text="Years of experience")
    
    # Skills and Education
    skills = TaggableManager(blank=True)
    education = RichTextField(blank=True)
    description = RichTextField()
    
    # SEO Fields
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Status and Dates
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    
    # History
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company_name}")
        if not self.meta_title:
            self.meta_title = self.title
        if not self.meta_description:
            self.meta_description = self.description[:160] if self.description else ""
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('jobs:job_detail', kwargs={'slug': self.slug})

    def get_salary_display(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,} - {self.salary_max:,}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,}+"
        elif self.salary_max:
            return f"Up to {self.salary_currency} {self.salary_max:,}"
        return "Salary not specified"

    def get_experience_display(self):
        if self.experience_min and self.experience_max:
            return f"{self.experience_min}-{self.experience_max} years"
        elif self.experience_min:
            return f"{self.experience_min}+ years"
        elif self.experience_max:
            return f"Up to {self.experience_max} years"
        return "Experience not specified"

    @property
    def is_expired(self):
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
            
    @property
    def short_description(self):
        """Returns a clean, truncated version of the job description for meta tags."""
        if not getattr(self, 'description', None):
            return f"{self.title} at {self.company_name} - {self.get_job_type_display()} position"
        # Remove HTML tags and extra whitespace
        import re
        clean_text = re.sub(r'<[^>]*>', ' ', str(self.description))
        clean_text = ' '.join(clean_text.split())
        return clean_text[:300]  # Return first 300 chars
        
    def get_share_image_absolute_url(self):
        from django.conf import settings
        from django.templatetags.static import static
        
        base_url = getattr(settings, 'SITE_URL', 'https://zeevikaconsultancy.com')
        
        # First try company logo
        if self.company_logo:
            return f"{base_url}{self.company_logo.url}"
            
        # Fallback to default share image
        default_image = static('images/og-default.jpg')
        return f"{base_url}{default_image}"
        return False


class CandidateApplication(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    total_experience = models.DecimalField(max_digits=4, decimal_places=1, help_text="Years of experience")
    cv = models.FileField(upload_to='applications/cv/', help_text="Upload CV/Resume (PDF, DOC, DOCX)")
    message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    is_shortlisted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    admin_notes = models.TextField(blank=True)
    
    # History
    history = HistoricalRecords()

    class Meta:
        ordering = ['-applied_at']
        unique_together = ['job', 'email']

    def __str__(self):
        return f"{self.name} - {self.job.title}"

    def get_absolute_url(self):
        return reverse('jobs:application_detail', kwargs={'pk': self.pk})

    @property
    def status(self):
        if self.is_rejected:
            return "Rejected"
        elif self.is_shortlisted:
            return "Shortlisted"
        return "Pending"
