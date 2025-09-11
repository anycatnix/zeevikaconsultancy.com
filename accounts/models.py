from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extended user profile model to store additional user information.
    This model is linked to the default User model via a OneToOne relationship.
    """
    USER_TYPE_CHOICES = (
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
    )
    
    # Required fields
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(
        max_length=10, 
        choices=USER_TYPE_CHOICES, 
        default='candidate',
        help_text="Determines if the user is a candidate or employer"
    )
    
    # Contact Information
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    
    # Profile Media
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        blank=True, 
        null=True,
        help_text="User's profile picture"
    )
    resume = models.FileField(
        upload_to='resumes/', 
        blank=True, 
        null=True,
        help_text="Candidate's resume/CV"
    )
    
    # Employer Specific Fields
    company_name = models.CharField(
        max_length=200, 
        blank=True, 
        null=True,
        help_text="Required if user_type is employer"
    )
    company_website = models.URLField(
        blank=True, 
        null=True,
        help_text="Company website (for employers)"
    )
    
    # Status and Timestamps
    is_verified = models.BooleanField(
        default=False,
        help_text="Email verification status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


# Signal to create/update user profile when User is saved
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal to automatically create a UserProfile when a new User is created
    and save the profile when the user is saved.
    """
    if created:
        UserProfile.objects.create(user=instance)
    instance.profile.save()

# Signal to manage user groups based on profile type
@receiver(post_save, sender=UserProfile)
def add_user_to_group(sender, instance, **kwargs):
    """
    Signal to add/remove user from appropriate groups based on user_type
    """
    employer_group, _ = Group.objects.get_or_create(name='Employers')
    
    if instance.user_type == 'employer':
        instance.user.groups.add(employer_group)
    else:
        if employer_group in instance.user.groups.all():
            instance.user.groups.remove(employer_group)
