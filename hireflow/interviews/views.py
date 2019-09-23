from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Interview
from .serializers import InterviewSerializer


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.select_related('application', 'interviewer').all()
    serializer_class = InterviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        application_id = self.request.query_params.get('application')
        interviewer_id = self.request.query_params.get('interviewer')
        completed = self.request.query_params.get('completed')
        if application_id:
            qs = qs.filter(application_id=application_id)
        if interviewer_id:
            qs = qs.filter(interviewer_id=interviewer_id)
        if completed is not None:
            qs = qs.filter(completed=completed.lower() == 'true')
        return qs.order_by('scheduled_at')
