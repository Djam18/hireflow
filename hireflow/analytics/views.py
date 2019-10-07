from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from pipeline.models import Application
from jobs.models import Job
from candidates.models import Candidate


class PipelineStatsView(APIView):
    """Analytics: candidates per pipeline stage."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stats = Application.objects.values('stage').annotate(
            count=Count('id')
        ).order_by('stage')

        result = {item['stage']: item['count'] for item in stats}
        result['total'] = Application.objects.count()
        return Response(result)


class JobStatsView(APIView):
    """Analytics: applications per job with stage breakdown."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        jobs = Job.objects.annotate(
            total_applications=Count('applications'),
            hired_count=Count('applications', filter=Q(applications__stage='HIRED')),
            rejected_count=Count('applications', filter=Q(applications__stage='REJECTED')),
            in_progress_count=Count(
                'applications',
                filter=~Q(applications__stage__in=['HIRED', 'REJECTED'])
            ),
        ).filter(total_applications__gt=0).order_by('-total_applications')

        data = []
        for job in jobs:
            data.append({
                'job_id': job.id,
                'title': job.title,
                'total_applications': job.total_applications,
                'hired': job.hired_count,
                'rejected': job.rejected_count,
                'in_progress': job.in_progress_count,
                'conversion_rate': (
                    round(job.hired_count / job.total_applications * 100, 1)
                    if job.total_applications > 0 else 0
                ),
            })
        return Response(data)


class RecruitingFunnelView(APIView):
    """Analytics: conversion rates between pipeline stages."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stages = ['NEW', 'SCREENING', 'INTERVIEW', 'OFFER', 'HIRED']
        counts = {}
        for stage in stages:
            counts[stage] = Application.objects.filter(stage=stage).count()

        rejected = Application.objects.filter(stage='REJECTED').count()

        funnel = []
        for i, stage in enumerate(stages):
            entry = {'stage': stage, 'count': counts[stage]}
            if i > 0 and counts[stages[i - 1]] > 0:
                entry['conversion_from_previous'] = round(
                    counts[stage] / counts[stages[i - 1]] * 100, 1
                )
            else:
                entry['conversion_from_previous'] = None
            funnel.append(entry)

        return Response({
            'funnel': funnel,
            'rejected_total': rejected,
        })


class CandidateSourceView(APIView):
    """Analytics: candidates added per month."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_count = Candidate.objects.filter(created_at__gte=thirty_days_ago).count()
        total_count = Candidate.objects.count()

        return Response({
            'total_candidates': total_count,
            'added_last_30_days': recent_count,
        })
