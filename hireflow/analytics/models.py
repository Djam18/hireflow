"""Analytics models — Django 5.2 LTS: composite primary keys.

Django 5.2 introduced CompositePrimaryKey for tables that have natural
composite PKs (e.g., many-to-many analytics tables).
"""
from __future__ import annotations

from django.db import models
from django.conf import settings


class HiringMetric(models.Model):
    """Recruitment metrics aggregated by job and date.

    Django 5.2: CompositePrimaryKey on (job, date) — no surrogate PK needed.
    """
    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='metrics')
    date = models.DateField()
    applications_count = models.IntegerField(default=0)
    screening_count = models.IntegerField(default=0)
    interview_count = models.IntegerField(default=0)
    offer_count = models.IntegerField(default=0)
    hire_count = models.IntegerField(default=0)

    # Django 5.2: composite PK replaces the implicit auto-increment id
    try:
        pk = models.CompositePrimaryKey('job', 'date')  # type: ignore[attr-defined]
    except AttributeError:
        # Django < 5.2 fallback — composite PK not available yet
        class Meta:
            unique_together = [('job', 'date')]

    def __str__(self) -> str:
        return f"HiringMetric(job={self.job_id}, date={self.date})"


class RecruitmentFunnel(models.Model):
    """Funnel conversion rates per recruiter and week."""
    recruiter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='funnel_stats',
    )
    week_start = models.DateField()
    applications_received = models.IntegerField(default=0)
    screened = models.IntegerField(default=0)
    interviewed = models.IntegerField(default=0)
    offered = models.IntegerField(default=0)
    hired = models.IntegerField(default=0)

    class Meta:
        unique_together = [('recruiter', 'week_start')]

    @property
    def screen_rate(self) -> float:
        if self.applications_received == 0:
            return 0.0
        return self.screened / self.applications_received

    @property
    def hire_rate(self) -> float:
        if self.applications_received == 0:
            return 0.0
        return self.hired / self.applications_received

    def __str__(self) -> str:
        return f"Funnel({self.recruiter_id}, week={self.week_start})"
