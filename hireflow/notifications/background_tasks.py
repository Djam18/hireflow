"""Django 6.0 native background tasks for simple notifications.

Django 6.0 introduced django.tasks — background tasks without a broker.
Tasks run after the HTTP response is sent, using the WSGI/ASGI thread pool.

Migration strategy:
- Simple tasks (welcome email, stage notification) → django.tasks
- Complex tasks (AI scoring, bulk processing) → stay on Celery

This module replaces the simple Celery tasks in tasks.py for Django 6.0.
"""
from __future__ import annotations

import logging

from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# Django 6.0 native background tasks
try:
    from django.tasks import background_task  # type: ignore[import]

    @background_task
    def send_welcome_email(candidate_email: str, candidate_name: str) -> None:
        """Send welcome email after candidate submits application.

        Runs after the HTTP response is sent — no delay for the user.
        """
        send_mail(
            subject="Application received — Hireflow",
            message=(
                f"Hi {candidate_name},\n\n"
                "We've received your application. We'll be in touch soon.\n\n"
                "Best regards,\nHireflow Team"
            ),
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hireflow.com'),
            recipient_list=[candidate_email],
            fail_silently=True,
        )
        logger.info("Welcome email sent to %s", candidate_email)

    @background_task
    def send_stage_notification(
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        new_stage: str,
    ) -> None:
        """Notify candidate of pipeline stage change via Django 6.0 background task.

        For Django < 6.0, falls back to the Celery task in tasks.py.
        """
        from .tasks import send_stage_change_email
        send_stage_change_email(candidate_email, candidate_name, job_title, new_stage)
        logger.info("Stage notification sent: %s → %s", candidate_email, new_stage)

except ImportError:
    # Django < 6.0: use Celery tasks (imported from tasks.py)
    logger.info("django.tasks not available, using Celery for notifications")

    def send_welcome_email(candidate_email: str, candidate_name: str) -> None:  # type: ignore[misc]
        from django.core.mail import send_mail
        send_mail(
            subject="Application received — Hireflow",
            message=f"Hi {candidate_name}, we received your application.",
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@hireflow.com'),
            recipient_list=[candidate_email],
            fail_silently=True,
        )

    def send_stage_notification(  # type: ignore[misc]
        candidate_email: str,
        candidate_name: str,
        job_title: str,
        new_stage: str,
    ) -> None:
        from .tasks import send_stage_change_email
        send_stage_change_email.delay(candidate_email, candidate_name, job_title, new_stage)
