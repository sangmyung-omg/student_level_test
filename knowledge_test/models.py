from django.db import models

class Problem(models.Model):
    uk_tag = models.CharField(max_length=200)
    problem = models.TextField()
    answer = models.IntegerField()
    
    def __str__(self):
        return self.uk_tag