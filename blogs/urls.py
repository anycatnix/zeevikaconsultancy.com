from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('search/', views.blog_search, name='blog_search'),
]
