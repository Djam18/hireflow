from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Candidate
from .serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all().order_by('-created_at')
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'last_name', 'email']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Candidate.objects.all()
        status = self.request.query_params.get('status', None)
        job = self.request.query_params.get('job', None)
        if status is not None:
            queryset = queryset.filter(status=status)
        if job is not None:
            queryset = queryset.filter(applications__job_id=job)
        return queryset.order_by('-created_at')
