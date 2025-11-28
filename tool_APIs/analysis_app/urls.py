# analysis_app/urls.py
from django.urls import path
from . import views

app_name = 'analysis'

urlpatterns = [
    # Dataset Analysis - main endpoint
    path('dataset-description/', views.dataset_description, name='dataset_description'),
    path('analyzer/', views.home_page, name='analyze'),
]