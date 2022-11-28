from django.db import models
from tenants.models import Company


class Candidate(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    linkedin_url = models.URLField(blank=True)
    resume = models.FileField(upload_to='resumes/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # Multi-tenant isolation
    company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.CASCADE, related_name='candidates')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
