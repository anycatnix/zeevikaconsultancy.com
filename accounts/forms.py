from django import forms
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile information.
    Includes both user and profile fields.
    """
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email',
            'phone', 'address', 'city', 'state', 'country', 'pincode',
            'profile_picture', 'resume', 'company_name', 'company_website'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize user fields
        if self.instance and hasattr(self.instance, 'user'):
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
            
            # Show/hide employer fields based on user type
            if self.instance.user_type != 'employer':
                self.fields.pop('company_name', None)
                self.fields.pop('company_website', None)
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        
        # Update user fields
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        
        if commit:
            user.save()
            profile.save()
        
        return profile

class UserTypeForm(forms.ModelForm):
    """
    Form for selecting user type during signup.
    This should be shown before the main registration form.
    """
    USER_TYPE_CHOICES = (
        ('candidate', 'I\'m looking for a job'),
        ('employer', 'I\'m looking to hire'),
    )
    
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='I am a...'
    )
    
    class Meta:
        model = UserProfile
        fields = ('user_type',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user_type'].widget.attrs.update({'class': 'form-radio'})
