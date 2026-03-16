from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom user model - extend as needed."""
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank = True)
    
    def __str__(self):
       return self.email or self.username 