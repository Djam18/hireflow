from django.contrib import admin
from .models import Application, StageHistory


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'job', 'stage', 'applied_at']
    list_filter = ['stage', 'job']
    search_fields = ['candidate__first_name', 'candidate__last_name', 'job__title']


@admin.register(StageHistory)
class StageHistoryAdmin(admin.ModelAdmin):
    list_display = ['application', 'from_stage', 'to_stage', 'changed_by', 'changed_at']
