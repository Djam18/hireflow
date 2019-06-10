from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'job_type', 'location', 'is_active', 'created_at', 'posted_by']
    list_filter = ['job_type', 'is_active', 'location']
    search_fields = ['title', 'description', 'location']
