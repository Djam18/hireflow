"""Tests for candidate and job endpoints."""
import pytest
from rest_framework import status
from .factories import CandidateFactory, JobFactory, ApplicationFactory, UserFactory


@pytest.mark.django_db
class TestCandidateAPI:
    def test_list_candidates_requires_auth(self, api_client):
        response = api_client.get('/api/candidates/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_candidates(self, auth_client):
        client, user = auth_client
        CandidateFactory.create_batch(5)
        response = client.get('/api/candidates/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5

    def test_create_candidate(self, auth_client):
        client, user = auth_client
        data = {
            'first_name': 'Alice',
            'last_name': 'Smith',
            'email': 'alice@example.com',
            'phone': '+1234567890',
        }
        response = client.post('/api/candidates/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['email'] == 'alice@example.com'

    def test_get_candidate(self, auth_client):
        client, user = auth_client
        candidate = CandidateFactory()
        response = client.get(f'/api/candidates/{candidate.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == candidate.email

    def test_update_candidate(self, auth_client):
        client, user = auth_client
        candidate = CandidateFactory()
        response = client.patch(
            f'/api/candidates/{candidate.id}/',
            {'phone': '+9876543210'},
            format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['phone'] == '+9876543210'

    def test_delete_candidate(self, auth_client):
        client, user = auth_client
        candidate = CandidateFactory()
        response = client.delete(f'/api/candidates/{candidate.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_search_candidate_by_name(self, auth_client):
        client, user = auth_client
        CandidateFactory(first_name='Alice', last_name='Smith', email='alice@test.com')
        CandidateFactory(first_name='Bob', last_name='Jones', email='bob@test.com')
        response = client.get('/api/candidates/?q=alice')
        assert response.status_code == status.HTTP_200_OK
        results = response.data['results']
        assert len(results) == 1
        assert results[0]['first_name'] == 'Alice'

    def test_filter_by_stage(self, auth_client):
        client, user = auth_client
        screening_app = ApplicationFactory(stage='SCREENING')
        interview_app = ApplicationFactory(stage='INTERVIEW')
        response = client.get('/api/candidates/?stage=SCREENING')
        assert response.status_code == status.HTTP_200_OK
        candidate_ids = [c['id'] for c in response.data['results']]
        assert screening_app.candidate.id in candidate_ids
        assert interview_app.candidate.id not in candidate_ids

    def test_duplicate_email_rejected(self, auth_client):
        client, user = auth_client
        CandidateFactory(email='unique@example.com')
        response = client.post('/api/candidates/', {
            'first_name': 'Bob',
            'last_name': 'Smith',
            'email': 'unique@example.com',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJobAPI:
    def test_list_jobs_requires_auth(self, api_client):
        response = api_client.get('/api/jobs/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_jobs(self, auth_client):
        client, user = auth_client
        JobFactory.create_batch(3, posted_by=user)
        response = client.get('/api/jobs/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 3

    def test_create_job(self, auth_client):
        client, user = auth_client
        data = {
            'title': 'Python Developer',
            'description': 'We need a Python expert.',
            'location': 'Remote',
            'job_type': 'FULL_TIME',
            'posted_by': user.id,
        }
        response = client.post('/api/jobs/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == 'Python Developer'

    def test_get_job(self, auth_client):
        client, user = auth_client
        job = JobFactory(posted_by=user)
        response = client.get(f'/api/jobs/{job.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == job.title

    def test_update_job(self, auth_client):
        client, user = auth_client
        job = JobFactory(posted_by=user)
        response = client.patch(f'/api/jobs/{job.id}/', {'is_active': False}, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['is_active'] is False

    def test_filter_active_jobs(self, auth_client):
        client, user = auth_client
        JobFactory(posted_by=user, is_active=True)
        JobFactory(posted_by=user, is_active=False)
        response = client.get('/api/jobs/?is_active=true')
        assert response.status_code == status.HTTP_200_OK
