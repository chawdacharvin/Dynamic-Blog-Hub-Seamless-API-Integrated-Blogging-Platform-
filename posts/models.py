from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=180, default=" Post Title")
    body = models.TextField(null=False, max_length=10000)
    created_on = models.DateTimeField(default=datetime.now, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    like = models.ManyToManyField(User, related_name="liked_post")
    dislike = models.ManyToManyField(User, related_name="dislike_post")

    def likes(self):
        return self.like.count()
    def dislikes(self):
        return self.dislike.count()
    def __str__(self):
        return f"{self.title} by {self.creator} on {self.created_on.strftime('%Y-%m-%d  %H:%M')}"
    
    
class Comment(models.Model):
    post = models.ForeignKey(Post,on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_on = models.DateTimeField(default=datetime.now)
    def __str__(self):
        return f"Comment by {self.user.username} on the post {self.post.title}"