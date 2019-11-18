from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.db.models import Q
from .models import Candidate
from .serializers import CandidateSerializer


class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all().order_by('-created_at')
    serializer_class = CandidateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    ordering_fields = ['created_at', 'last_name', 'email']
    ordering = ['-created_at']
    search_fields = ['first_name', 'last_name', 'email']

    def get_queryset(self):
        queryset = Candidate.objects.all()
        job = self.request.query_params.get('job', None)
        stage = self.request.query_params.get('stage', None)
        search = self.request.query_params.get('q', None)

        if job is not None:
            queryset = queryset.filter(applications__job_id=job)
        if stage is not None:
            queryset = queryset.filter(applications__stage=stage)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        return queryset.order_by('-created_at').distinct()

    @action(detail=False, methods=['get'], url_path='by-stage')
    def by_stage(self, request):
        """Return candidates grouped by their current pipeline stage."""
        from pipeline.models import Application
        stages = Application.Stage.choices
        result = {}
        for stage_value, stage_label in stages:
            candidates = Candidate.objects.filter(
                applications__stage=stage_value
            ).distinct()
            result[stage_value] = CandidateSerializer(candidates, many=True).data
        return Response(result)

    @action(detail=False, methods=['post'], url_path='bulk-delete')
    def bulk_delete(self, request):
        """Delete multiple candidates by IDs."""
        ids = request.data.get('ids', [])
        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count, _ = Candidate.objects.filter(id__in=ids).delete()
        return Response({'deleted': deleted_count})

    @action(detail=False, methods=['post'], url_path='bulk-tag')
    def bulk_tag(self, request):
        """Add a tag/note to multiple candidates (basic implementation)."""
        ids = request.data.get('ids', [])
        note = request.data.get('note', '')
        if not ids:
            return Response({'error': 'No IDs provided'}, status=status.HTTP_400_BAD_REQUEST)

        # basic: just return which candidates were targeted
        candidates = Candidate.objects.filter(id__in=ids)
        return Response({
            'updated': candidates.count(),
            'note': note,
            'candidate_ids': list(candidates.values_list('id', flat=True)),
        })
