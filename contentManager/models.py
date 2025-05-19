import os
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone 

class PostBlog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return self.title if self.title else f"Post #{self.id}"

class Attachment(models.Model):
    post = models.ForeignKey(PostBlog, on_delete=models.CASCADE)  # Linking each attachment to a post
    file = models.FileField(upload_to='attachments/')   # will upload to media/attachments

    def save(self, *args, **kwargs):
        # Generate unique filename with post ID key
        filename, extension = os.path.splitext(self.file.name)
        self.file.name = f"{self.post.id}_{filename}{extension}"
        super().save(*args, **kwargs) 


class Sliders(models.Model):
    img = models.FileField(upload_to='slider/')
    smallText = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    info = models.TextField()    
    
    def __str__(self):
        return self.smallText