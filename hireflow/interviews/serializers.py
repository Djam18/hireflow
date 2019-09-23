from rest_framework import serializers
from .models import Interview


class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = [
            'id', 'application', 'interviewer', 'interview_type',
            'scheduled_at', 'duration_minutes', 'location', 'notes',
            'completed', 'created_at'
        ]
        read_only_fields = ['created_at']

    def validate(self, attrs):
        interviewer = attrs.get('interviewer')
        scheduled_at = attrs.get('scheduled_at')
        duration_minutes = attrs.get('duration_minutes', 60)
        exclude_id = self.instance.id if self.instance else None

        if interviewer and scheduled_at:
            has_conflict = Interview.check_conflict(
                interviewer=interviewer,
                scheduled_at=scheduled_at,
                duration_minutes=duration_minutes,
                exclude_id=exclude_id,
            )
            if has_conflict:
                raise serializers.ValidationError(
                    "The interviewer already has an interview scheduled at this time."
                )
        return attrs
