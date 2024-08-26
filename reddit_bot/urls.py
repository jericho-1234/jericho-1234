# myapp/urls.py
from django.urls import path
from .views import get_posts

urlpatterns = [
    path('', get_posts, name='get_posts'),
]
