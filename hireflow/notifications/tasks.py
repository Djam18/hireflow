from celery import shared_task
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings


# Celery 5.0: autoretry_for replaces manual self.retry() boilerplate
@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def send_stage_change_email(candidate_email, candidate_name, job_title, new_stage):
    """Send email notification when a candidate moves to a new pipeline stage.

    Args:
        candidate_email: Recipient email address.
        candidate_name: Full name of the candidate.
        job_title: Title of the job position.
        new_stage: The new pipeline stage name.
    """
    stage_messages = {
        'SCREENING': "Your application is moving to the screening phase.",
        'INTERVIEW': "Congratulations! You've been selected for an interview.",
        'OFFER': "We are pleased to extend an offer for this position.",
        'HIRED': "Welcome to the team! Your application has been accepted.",
        'REJECTED': "Thank you for your interest. We will not be moving forward at this time.",
    }

    message = stage_messages.get(new_stage, f"Your application status has been updated to {new_stage}.")

    send_mail(
        subject=f"Application Update: {job_title}",
        message=f"Dear {candidate_name},\n\n{message}\n\nBest regards,\nHireflow Team",
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hireflow.com'),
        recipient_list=[candidate_email],
        fail_silently=True,
    )

    return {"sent": True, "to": candidate_email, "stage": new_stage}


@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def send_interview_reminder(candidate_email, candidate_name, job_title, interview_time):
    """Send interview reminder 24 hours before scheduled time.

    Args:
        candidate_email: Candidate email address.
        candidate_name: Full name of the candidate.
        job_title: Position title.
        interview_time: ISO format datetime string.
    """
    send_mail(
        subject=f"Interview Reminder: {job_title}",
        message=(
            f"Dear {candidate_name},\n\n"
            f"This is a reminder of your interview for {job_title} "
            f"scheduled for {interview_time}.\n\n"
            "Best regards,\nHireflow Team"
        ),
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hireflow.com'),
        recipient_list=[candidate_email],
        fail_silently=True,
    )

    return {"sent": True, "to": candidate_email}
