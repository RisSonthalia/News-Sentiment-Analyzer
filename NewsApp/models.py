from django.db import models
from django.contrib.auth.models import User

class SearchQueries(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=200)
    positive_articles = models.PositiveIntegerField(default=0)
    neutral_articles = models.PositiveIntegerField(default=0)
    negative_articles = models.PositiveIntegerField(default=0)
    search_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.keyword}"

class Review(models.Model):
    stars = models.IntegerField()  # Assuming stars can be 1-5
    review_text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Review by {self.user.username} on {self.datetime}'
