from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Job listing and search
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('jobs/<slug:slug>/', views.JobDetailView.as_view(), name='job_detail'),
    
    # Job application
    path('jobs/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    
    # Category, subcategory, and functional area views
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('subcategory/<slug:slug>/', views.subcategory_detail, name='subcategory_detail'),
    path('functional-area/<slug:slug>/', views.functional_area_detail, name='functional_area_detail'),
    
    # Admin views for applications
    path('applications/', views.ApplicationListView.as_view(), name='application_list'),
    path('applications/<int:pk>/', views.ApplicationDetailView.as_view(), name='application_detail'),
    
    # AJAX views for dynamic dropdowns
    path('ajax/load-cities/', views.load_cities, name='load_cities'),
    path('ajax/load-subcategories/', views.load_subcategories, name='load_subcategories'),
    path('ajax/load-functional-areas/', views.load_functional_areas, name='load_functional_areas'),
]
