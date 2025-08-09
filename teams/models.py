from django.db import models
from django.utils import timezone


class Conference(models.Model):
    """NHL Conference (Eastern, Western)"""
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Division(models.Model):
    """NHL Division (Atlantic, Metropolitan, Central, Pacific)"""
    name = models.CharField(max_length=50, unique=True)
    abbreviation = models.CharField(max_length=10, unique=True)
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='divisions')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.conference.name})"

    class Meta:
        ordering = ['conference__name', 'name']


class Team(models.Model):
    """NHL Team"""
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, unique=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams')

    # Team details
    founded_year = models.PositiveIntegerField(null=True, blank=True)
    arena_name = models.CharField(max_length=200, blank=True)
    arena_capacity = models.PositiveIntegerField(null=True, blank=True)

    # Colors and branding
    primary_color = models.CharField(max_length=7, blank=True)  # Hex color
    secondary_color = models.CharField(max_length=7, blank=True)  # Hex color
    logo_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.city} {self.name}"

    @property
    def full_name(self):
        return f"{self.city} {self.name}"

    @property
    def conference(self):
        return self.division.conference

    class Meta:
        ordering = ['city', 'name']
        unique_together = ['city', 'name']


class Season(models.Model):
    """NHL Season"""
    name = models.CharField(max_length=20, unique=True)  # e.g., "2024-25"
    start_date = models.DateField()
    end_date = models.DateField()
    playoffs_start_date = models.DateField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Ensure only one season is marked as current
        if self.is_current:
            Season.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-start_date']
