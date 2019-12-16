from rest_framework import serializers
from .models import Candidate


class CandidateSerializer(serializers.ModelSerializer):
    """Serializer for Candidate model.

    Note: fields='__all__' still in use — will be replaced with explicit
    fields list in a future refactor.
    """

    class Meta:
        model = Candidate
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
