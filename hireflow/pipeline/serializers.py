from rest_framework import serializers
from .models import Application, StageHistory


class StageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = StageHistory
        fields = ['id', 'from_stage', 'to_stage', 'changed_by', 'changed_at', 'notes']


class ApplicationSerializer(serializers.ModelSerializer):
    history = StageHistorySerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = ['id', 'candidate', 'job', 'stage', 'notes', 'applied_at', 'updated_at', 'history']
        read_only_fields = ['applied_at', 'updated_at']


class TransitionSerializer(serializers.Serializer):
    new_stage = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_new_stage(self, value):
        valid = ['NEW', 'SCREENING', 'INTERVIEW', 'OFFER', 'HIRED', 'REJECTED']
        if value not in valid:
            raise serializers.ValidationError(f"Invalid stage: {value}")
        return value
