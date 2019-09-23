from django.contrib import admin
from .models import Interview


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ['application', 'interviewer', 'interview_type', 'scheduled_at', 'completed']
    list_filter = ['interview_type', 'completed']
