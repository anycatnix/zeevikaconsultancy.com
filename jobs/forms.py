from django import forms
from django.core.exceptions import ValidationError
from .models import CandidateApplication, JobPost


class CandidateApplicationForm(forms.ModelForm):
    class Meta:
        model = CandidateApplication
        fields = ['name', 'email', 'phone', 'total_experience', 'cv', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Your Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'your.email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': '+1 (555) 123-4567'
            }),
            'total_experience': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Years of experience',
                'step': '0.1',
                'min': '0'
            }),
            'cv': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'accept': '.pdf,.doc,.docx'
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Tell us why you are interested in this position...'
            }),
        }

    def clean_cv(self):
        cv = self.cleaned_data.get('cv')
        if cv:
            # Check file size (5MB limit)
            if cv.size > 5 * 1024 * 1024:
                raise ValidationError("CV file size must be less than 5MB.")
            
            # Check file extension
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_extension = cv.name.lower()
            if not any(file_extension.endswith(ext) for ext in allowed_extensions):
                raise ValidationError("Please upload a PDF, DOC, or DOCX file.")
        
        return cv

    def clean_total_experience(self):
        experience = self.cleaned_data.get('total_experience')
        if experience and experience < 0:
            raise ValidationError("Experience cannot be negative.")
        return experience


class JobSearchForm(forms.Form):
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Job title, keywords, or company'
        })
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'City, state, or remote'
        })
    )
    job_type = forms.ChoiceField(
        choices=[('', 'All Types')] + JobPost.JOB_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    experience_level = forms.ChoiceField(
        choices=[
            ('', 'All Levels'),
            ('entry', 'Entry Level (0-2 years)'),
            ('mid', 'Mid Level (3-5 years)'),
            ('senior', 'Senior Level (6+ years)'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
