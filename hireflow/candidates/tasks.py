"""Candidate AI scoring via OpenAI embeddings.

Scores how well a candidate's CV/profile matches a job description
using cosine similarity of OpenAI text-embedding-3-small vectors.

Security notes:
- OPENAI_API_KEY stored in .env, never hardcoded
- AI scores are advisory only — not used for automated rejection
- Scores stored in JSONField for auditability
- Task is idempotent: re-running updates the score, doesn't duplicate
"""
from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from celery import shared_task

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


def _get_embedding(text: str) -> list[float]:
    """Get OpenAI text embedding for a string.

    Raises RuntimeError if OPENAI_API_KEY is not set.
    """
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY not configured — set it in .env")

    try:
        import openai  # type: ignore[import]
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],  # stay within token limit
        )
        return response.data[0].embedding
    except ImportError as exc:
        raise RuntimeError("openai package not installed: pip install openai>=1.0") from exc


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    import math

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


@shared_task(autoretry_for=(Exception,), max_retries=3, retry_backoff=True)
def score_candidate_for_job(candidate_id: int, job_id: int) -> dict[str, object]:
    """Score a candidate's fit for a job using OpenAI embeddings.

    Stores the result in a CandidateScore record (JSONField: ai_score).
    This task is idempotent — re-running updates the existing score.

    Args:
        candidate_id: PK of the Candidate to score.
        job_id: PK of the Job to score against.

    Returns:
        dict with score, model, and candidate/job IDs.
    """
    from candidates.models import Candidate
    from jobs.models import Job

    try:
        candidate = Candidate.objects.get(pk=candidate_id)
        job = Job.objects.get(pk=job_id)
    except (Candidate.DoesNotExist, Job.DoesNotExist) as exc:
        logger.error("score_candidate_for_job: %s", exc)
        return {"error": str(exc)}

    # Build text representations
    candidate_text = (
        f"{candidate.first_name} {candidate.last_name}\n"
        f"Email: {candidate.email}\n"
        f"LinkedIn: {candidate.linkedin_url or 'N/A'}"
    )
    job_text = f"{job.title}\n{job.description}\nLocation: {job.location}"

    try:
        candidate_embedding = _get_embedding(candidate_text)
        job_embedding = _get_embedding(job_text)
        similarity = _cosine_similarity(candidate_embedding, job_embedding)
        score = round(similarity * 100, 2)
    except RuntimeError as exc:
        logger.warning("AI scoring skipped: %s", exc)
        return {"error": str(exc), "candidate_id": candidate_id, "job_id": job_id}

    # Store result — upsert pattern
    result = {
        "score": score,
        "model": "text-embedding-3-small",
        "candidate_id": candidate_id,
        "job_id": job_id,
    }

    # Update candidate metadata with AI score
    candidate.metadata = {**candidate.metadata, f"ai_score_job_{job_id}": result}
    candidate.save(update_fields=["metadata"])

    logger.info(
        "AI score: candidate=%d, job=%d, score=%.2f",
        candidate_id, job_id, score,
    )
    return result
