from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, update_session_auth_hash
from django.contrib import messages
from django.views.generic import TemplateView, UpdateView, FormView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.models import User
from .models import UserProfile
from .forms import UserProfileForm, UserTypeForm

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        # Add any additional context data here
        return context

class SettingsView(LoginRequiredMixin, UpdateView):
    """
    View for editing user profile and settings.
    Handles both user and profile information.
    """
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/settings.html'
    success_url = reverse_lazy('accounts:settings')
    
    def get_object(self):
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.get_object()
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Your profile was successfully updated!')
        return response


def signup(request):
    """
    Custom signup view that handles both candidate and employer registration.
    Uses a two-step process: first select user type, then fill in details.
    """
    # If user is already authenticated, redirect to profile
    if request.user.is_authenticated:
        return redirect('accounts:profile')
    
    # Step 1: User type selection
    if 'user_type' not in request.session:
        if request.method == 'POST':
            form = UserTypeForm(request.POST)
            if form.is_valid():
                request.session['user_type'] = form.cleaned_data['user_type']
                return redirect('accounts:signup')
        else:
            form = UserTypeForm()
        
        return render(request, 'registration/select_user_type.html', {'form': form})
    
    # Step 2: User registration
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = request.POST.get('email', '')
            user.first_name = request.POST.get('first_name', '')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            
            # Get or create user profile with selected type
            user_type = request.session.pop('user_type', 'candidate')
            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    'user_type': user_type,
                    'company_name': request.POST.get('company_name', '') if user_type == 'employer' else ''
                }
            )
            
            # Log the user in
            login(request, user)
            messages.success(request, 'Registration successful! Please complete your profile.')
            return redirect('accounts:settings')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {
        'form': form,
        'is_employer': request.session.get('user_type') == 'employer'
    })

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:settings')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
