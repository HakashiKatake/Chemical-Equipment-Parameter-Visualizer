"""
Database models for Chemical Equipment Parameter Visualizer
"""
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Dataset(models.Model):
    """
    Represents an uploaded CSV dataset.
    Stores metadata only; equipment data is stored in Equipment model.
    Automatically maintains last 5 datasets per user.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    row_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-uploaded_at']
        
    def __str__(self):
        return f"{self.filename} by {self.user.username} at {self.uploaded_at}"
    
    def save(self, *args, **kwargs):
        """Override save to enforce dataset limit per user"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # Get all datasets for this user, ordered by upload time (newest first)
            user_datasets = Dataset.objects.filter(user=self.user).order_by('-uploaded_at')
            
            # If more than MAX_DATASETS_PER_USER, delete the oldest ones
            if user_datasets.count() > settings.MAX_DATASETS_PER_USER:
                datasets_to_delete = user_datasets[settings.MAX_DATASETS_PER_USER:]
                for dataset in datasets_to_delete:
                    dataset.delete()


class Equipment(models.Model):
    """
    Represents a single equipment entry from CSV.
    Uses normalized field names internally.
    """
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)  # Normalized: lowercase, underscores
    flowrate = models.FloatField()  # m³/h
    pressure = models.FloatField()  # bar
    temperature = models.FloatField()  # °C
    
    class Meta:
        ordering = ['equipment_name']
        
    def __str__(self):
        return f"{self.equipment_name} ({self.type})"
