from django.db import models
from django.conf import settings
from pipeline.models import Application


class Interview(models.Model):
    class InterviewType(models.TextChoices):
        PHONE = 'PHONE', 'Phone Screen'
        TECHNICAL = 'TECHNICAL', 'Technical'
        BEHAVIORAL = 'BEHAVIORAL', 'Behavioral'
        FINAL = 'FINAL', 'Final Round'

    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='interviews'
    )
    interview_type = models.CharField(max_length=20, choices=InterviewType.choices, default=InterviewType.PHONE)
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField(default=60)
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.application} - {self.interview_type} at {self.scheduled_at}"

    @classmethod
    def check_conflict(cls, interviewer, scheduled_at, duration_minutes, exclude_id=None):
        """Check if the interviewer has a conflicting interview scheduled.

        Args:
            interviewer: User instance.
            scheduled_at: datetime of the interview start.
            duration_minutes: Duration of the interview.
            exclude_id: Interview ID to exclude (for updates).

        Returns:
            True if conflict exists, False otherwise.
        """
        from datetime import timedelta
        end_time = scheduled_at + timedelta(minutes=duration_minutes)

        qs = cls.objects.filter(
            interviewer=interviewer,
            completed=False,
        )
        if exclude_id:
            qs = qs.exclude(id=exclude_id)

        for interview in qs:
            from datetime import timedelta as td
            interview_end = interview.scheduled_at + td(minutes=interview.duration_minutes)
            if scheduled_at < interview_end and end_time > interview.scheduled_at:
                return True
        return False
