from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Task(models.Model):
    CATEGORY_CHOICES = [
        ('work', 'Work'),
        ('personal', 'Personal'),
        ('study', 'Study'),
        ('other', 'Other'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=6, choices=PRIORITY_CHOICES, default='medium')
    due_date = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-due_date', '-created_at']
        verbose_name_plural = 'tasks'

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date and not self.is_completed:
            return self.due_date < timezone.now()
        return False

    @property
    def completion_percentage(self):
        if self.is_completed:
            return 100
        return 0