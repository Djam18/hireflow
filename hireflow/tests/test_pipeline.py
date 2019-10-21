"""Tests for pipeline transitions and permission enforcement."""
import pytest
from rest_framework import status
from .factories import UserFactory, ApplicationFactory, CandidateFactory, JobFactory
from pipeline.models import Application, StageHistory


@pytest.mark.django_db
class TestApplicationAPI:
    def test_list_applications_requires_auth(self, api_client):
        response = api_client.get('/api/applications/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_applications_authenticated(self, auth_client):
        client, user = auth_client
        ApplicationFactory.create_batch(3)
        response = client.get('/api/applications/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_application(self, auth_client):
        client, user = auth_client
        job = JobFactory(posted_by=user)
        candidate = CandidateFactory()
        response = client.post('/api/applications/', {
            'candidate': candidate.id,
            'job': job.id,
            'stage': 'NEW',
        })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['stage'] == 'NEW'

    def test_filter_by_stage(self, auth_client):
        client, user = auth_client
        ApplicationFactory(stage='SCREENING')
        ApplicationFactory(stage='INTERVIEW')
        ApplicationFactory(stage='NEW')
        response = client.get('/api/applications/?stage=SCREENING')
        assert response.status_code == status.HTTP_200_OK
        assert all(a['stage'] == 'SCREENING' for a in response.data['results'])


@pytest.mark.django_db
class TestApplicationTransition:
    def test_valid_transition(self, auth_client):
        client, user = auth_client
        app = ApplicationFactory(stage='NEW')
        response = client.post(
            f'/api/applications/{app.id}/transition/',
            {'new_stage': 'SCREENING'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['stage'] == 'SCREENING'
        app.refresh_from_db()
        assert app.stage == 'SCREENING'

    def test_invalid_transition_rejected(self, auth_client):
        client, user = auth_client
        app = ApplicationFactory(stage='NEW')
        response = client.post(
            f'/api/applications/{app.id}/transition/',
            {'new_stage': 'HIRED'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_transition_creates_history(self, auth_client):
        client, user = auth_client
        app = ApplicationFactory(stage='NEW')
        client.post(
            f'/api/applications/{app.id}/transition/',
            {'new_stage': 'SCREENING'},
            format='json'
        )
        history = StageHistory.objects.filter(application=app)
        assert history.count() == 1
        assert history.first().from_stage == 'NEW'
        assert history.first().to_stage == 'SCREENING'

    def test_transition_records_user(self, auth_client):
        client, user = auth_client
        app = ApplicationFactory(stage='NEW')
        client.post(
            f'/api/applications/{app.id}/transition/',
            {'new_stage': 'SCREENING'},
            format='json'
        )
        history = StageHistory.objects.get(application=app)
        assert history.changed_by == user

    def test_full_happy_path_new_to_hired(self, auth_client):
        client, user = auth_client
        app = ApplicationFactory(stage='NEW')

        stages = ['SCREENING', 'INTERVIEW', 'OFFER', 'HIRED']
        current = 'NEW'
        for next_stage in stages:
            response = client.post(
                f'/api/applications/{app.id}/transition/',
                {'new_stage': next_stage},
                format='json'
            )
            assert response.status_code == status.HTTP_200_OK, f"Failed: {current} -> {next_stage}"
            current = next_stage

        app.refresh_from_db()
        assert app.stage == 'HIRED'
        assert StageHistory.objects.filter(application=app).count() == 4

    def test_transition_to_rejected_from_any_stage(self, auth_client):
        client, user = auth_client
        for stage in ['NEW', 'SCREENING', 'INTERVIEW', 'OFFER']:
            app = ApplicationFactory(stage=stage)
            response = client.post(
                f'/api/applications/{app.id}/transition/',
                {'new_stage': 'REJECTED'},
                format='json'
            )
            assert response.status_code == status.HTTP_200_OK

    def test_cannot_transition_from_hired(self, auth_client):
        client, user = auth_client
        app = ApplicationFactory(stage='HIRED')
        response = client.post(
            f'/api/applications/{app.id}/transition/',
            {'new_stage': 'REJECTED'},
            format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
