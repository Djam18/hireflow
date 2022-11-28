from django.db import models
from django.conf import settings
from tenants.models import Company


class JobType(models.TextChoices):
    FULL_TIME = 'FULL_TIME', 'Full Time'
    PART_TIME = 'PART_TIME', 'Part Time'
    CONTRACT = 'CONTRACT', 'Contract'
    INTERNSHIP = 'INTERNSHIP', 'Internship'


class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    location = models.CharField(max_length=200)
    salary_min = models.IntegerField(null=True, blank=True)
    salary_max = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Multi-tenant isolation: every job belongs to one company
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='jobs')

    def __str__(self):
        return self.title
