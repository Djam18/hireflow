from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StageHistory
from notifications.tasks import send_stage_change_email


@receiver(post_save, sender=StageHistory)
def on_stage_change(sender, instance, created, **kwargs):
    """Fire email notification when a stage history entry is created."""
    if not created:
        return

    candidate = instance.application.candidate
    job = instance.application.job

    send_stage_change_email.delay(
        candidate_email=candidate.email,
        candidate_name=f"{candidate.first_name} {candidate.last_name}",
        job_title=job.title,
        new_stage=instance.to_stage,
    )
