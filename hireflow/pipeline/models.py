from django.db import models
from django.conf import settings
from candidates.models import Candidate
from jobs.models import Job


ALLOWED_TRANSITIONS = {
    'NEW': ['SCREENING', 'REJECTED'],
    'SCREENING': ['INTERVIEW', 'REJECTED'],
    'INTERVIEW': ['OFFER', 'REJECTED'],
    'OFFER': ['HIRED', 'REJECTED'],
    'HIRED': [],
    'REJECTED': [],
}


class Application(models.Model):
    class Stage(models.TextChoices):
        NEW = 'NEW', 'New'
        SCREENING = 'SCREENING', 'Screening'
        INTERVIEW = 'INTERVIEW', 'Interview'
        OFFER = 'OFFER', 'Offer'
        HIRED = 'HIRED', 'Hired'
        REJECTED = 'REJECTED', 'Rejected'

    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.NEW)
    notes = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='updated_applications'
    )

    class Meta:
        unique_together = [['candidate', 'job']]

    def can_transition_to(self, new_stage):
        allowed = ALLOWED_TRANSITIONS.get(self.stage, [])
        return new_stage in allowed

    def transition_to(self, new_stage, user=None):
        if not self.can_transition_to(new_stage):
            raise ValueError(
                f"Invalid transition: {self.stage} -> {new_stage}. "
                f"Allowed: {ALLOWED_TRANSITIONS.get(self.stage, [])}"
            )
        self.stage = new_stage
        if user:
            self.updated_by = user
        self.save()

    def __str__(self):
        return f"{self.candidate} — {self.job} ({self.stage})"


class StageHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='history')
    from_stage = models.CharField(max_length=20)
    to_stage = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.application} : {self.from_stage} -> {self.to_stage}"
