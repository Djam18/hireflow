from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from .models import Job
from .serializers import JobSerializer


class JobViewSet(viewsets.ModelViewSet):
    """CRUD for job postings.

    Supports filtering by is_active, ordering by created_at.
    Only authenticated users can access.
    """
    queryset = Job.objects.all().order_by('-created_at')
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'title', 'salary_min']

    def get_queryset(self):
        qs = super().get_queryset()
        is_active = self.request.query_params.get('is_active')
        job_type = self.request.query_params.get('job_type')
        if is_active is not None:
            qs = qs.filter(is_active=is_active.lower() == 'true')
        if job_type:
            qs = qs.filter(job_type=job_type)
        return qs

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)
