from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Application, StageHistory
from .serializers import ApplicationSerializer, TransitionSerializer
from notifications.tasks import send_stage_change_email


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related('candidate', 'job').all()
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        job_id = self.request.query_params.get('job')
        stage = self.request.query_params.get('stage')
        if job_id:
            qs = qs.filter(job_id=job_id)
        if stage:
            qs = qs.filter(stage=stage)
        return qs

    @action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        application = self.get_object()
        serializer = TransitionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        new_stage = serializer.validated_data['new_stage']
        notes = serializer.validated_data.get('notes', '')
        old_stage = application.stage

        try:
            application.transition_to(new_stage, user=request.user)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        StageHistory.objects.create(
            application=application,
            from_stage=old_stage,
            to_stage=new_stage,
            changed_by=request.user,
            notes=notes,
        )

        candidate = application.candidate
        send_stage_change_email.delay(
            candidate_email=candidate.email,
            candidate_name=f"{candidate.first_name} {candidate.last_name}",
            job_title=application.job.title,
            new_stage=new_stage,
        )

        return Response(ApplicationSerializer(application).data)
