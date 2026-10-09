from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=18)
    email = models.EmailField(blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatar/',blank=True)
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.nickname

class Articles(models.Model):
    author = models.ForeignKey(Member, on_delete=models.CASCADE,related_name='article')
    title = models.CharField(max_length=80)
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.IntegerField(default=0)


    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Comments(models.Model):
    content = models.TextField()
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    commenter = models.ForeignKey(Member, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.commenter} - {self.content[0:20]}"

    class Meta:
        ordering = ['id']