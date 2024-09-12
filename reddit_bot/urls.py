# myapp/urls.py
from django.urls import path
from .views import get_posts_and_generate_response

urlpatterns = [
    path('', get_posts_and_generate_response, name='get_posts_and_generate_response'),
]
