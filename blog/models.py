from django.db import models
from django.core import exceptions
from django.contrib.auth.models import User
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField
from read_statistics.models import ReadNumExpandMethod

# Create your models here.
class BlogType(models.Model):
    type_name = models.CharField(max_length=30)

    def __str__(self):
        return self.type_name

class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=30)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    content = RichTextUploadingField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return '<blog: %s>' % self.title

    def get_user(self):
        return self.author

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk':self.pk})

    class Meta:
        ordering = ['-created_time']