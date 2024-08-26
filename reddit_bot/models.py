from django.db import models

# Create your models here.
from django.db import models

class RedditPost(models.Model):
    post_id = models.CharField(max_length=30, unique=True)
    title = models.CharField(max_length=300)
    content = models.TextField()

class GeneratedResponse(models.Model):
    post = models.ForeignKey(RedditPost, on_delete=models.CASCADE)
    response_text = models.TextField()
