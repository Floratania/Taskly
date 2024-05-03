from django.db import models

from django.contrib.auth.models import User
from django.urls import reverse



class Task(models.Model):
    
    STATUS_CHOICES = [
        ('option1','Assigned'),
        ('option2','In progress'),
        ('option3','Done'),
        
    ]
    
    title = models.CharField(max_length=100, null=True)
    
    content = models.CharField(max_length=1000, null=True, blank=True)
    
    date_posted = models.DateTimeField(auto_now_add=True, null=True)
    
    date_end = models.DateTimeField(null=True)
    
    do_to = models.DateTimeField(null=True)
    
    status = models.CharField(max_length=100, null=True, choices=STATUS_CHOICES)
    
    user = models.ForeignKey(User, max_length=18, on_delete=models. CASCADE, null=True)
    
    def __str__(self):
        return self.title
    
    @property
    def get_html_url(self):
        url = reverse('cal:event_edit', args=(self.id,))
        return f'<a href="{url}"> {self.title} </a>'
    
    
    def get_total_by_status(self):
        total = Task.objects.filter(status=self.status).count()
        return total


class Profile(models.Model):
    
    profile_pic = models.ImageField(null=True, blank=True, upload_to="images/", default='Default.jpg')
    
    user = models.ForeignKey(User, max_length=18, on_delete=models.CASCADE, null=True)
    
    phone_number = models.CharField(max_length=15, blank=True)
    
    def __str__(self):
        return self.user.username
    
    
class Activity(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    
    last_login = models.DateTimeField(null=True, blank=True)
    
    last_logout = models.DateTimeField(null=True, blank=True)
    
    total_tasks_completed = models.IntegerField(default=0)
    
    total_tasks_assigned = models.IntegerField(default=0)
    
    total_tasks_in_progress = models.IntegerField(default=0)