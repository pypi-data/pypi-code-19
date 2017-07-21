from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Snippet(models.Model):
    title = models.CharField(max_length=20, default='hello')
    description = models.CharField(max_length=20)
    owner = models.ForeignKey('auth.User', related_name='snippets', on_delete=models.CASCADE)
    # owner = models.CharField(max_length=10, default='owner')

    def __unicode__(self):
        return self.title

# {"title": "h","description": "9"}
