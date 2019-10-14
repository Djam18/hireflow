"""Basic model tests using factories."""
import pytest
from .factories import UserFactory, JobFactory, CandidateFactory, ApplicationFactory
from pipeline.models import Application, ALLOWED_TRANSITIONS


@pytest.mark.django_db
class TestCustomUser:
    def test_create_user(self):
        user = UserFactory()
        assert user.id is not None
        assert user.is_active
        assert user.check_password('testpass123')

    def test_user_role_default(self):
        from accounts.models import CustomUser
        user = UserFactory()
        assert user.role == CustomUser.Role.RECRUITER

    def test_user_str(self):
        user = UserFactory(username='alice')
        assert str(user) == 'alice'


@pytest.mark.django_db
class TestJob:
    def test_create_job(self):
        job = JobFactory()
        assert job.id is not None
        assert job.is_active

    def test_job_str(self):
        job = JobFactory(title='Senior Engineer')
        assert str(job) == 'Senior Engineer'


@pytest.mark.django_db
class TestCandidate:
    def test_create_candidate(self):
        candidate = CandidateFactory()
        assert candidate.id is not None
        assert '@' in candidate.email

    def test_candidate_str(self):
        candidate = CandidateFactory(first_name='Alice', last_name='Smith')
        assert str(candidate) == 'Alice Smith'


@pytest.mark.django_db
class TestApplication:
    def test_create_application(self):
        app = ApplicationFactory()
        assert app.id is not None
        assert app.stage == Application.Stage.NEW

    def test_application_str(self):
        app = ApplicationFactory()
        assert app.candidate.first_name in str(app) or app.stage in str(app)

    def test_allowed_transitions_new(self):
        assert 'SCREENING' in ALLOWED_TRANSITIONS['NEW']
        assert 'REJECTED' in ALLOWED_TRANSITIONS['NEW']
        assert 'OFFER' not in ALLOWED_TRANSITIONS['NEW']

    def test_can_transition_to(self):
        app = ApplicationFactory(stage='NEW')
        assert app.can_transition_to('SCREENING') is True
        assert app.can_transition_to('OFFER') is False

    def test_transition_to_valid_stage(self):
        app = ApplicationFactory(stage='NEW')
        app.transition_to('SCREENING')
        app.refresh_from_db()
        assert app.stage == 'SCREENING'

    def test_transition_to_invalid_raises(self):
        app = ApplicationFactory(stage='NEW')
        with pytest.raises(ValueError, match="Invalid transition"):
            app.transition_to('HIRED')

    def test_hired_has_no_transitions(self):
        assert ALLOWED_TRANSITIONS['HIRED'] == []

    def test_rejected_has_no_transitions(self):
        assert ALLOWED_TRANSITIONS['REJECTED'] == []

    def test_unique_together_candidate_job(self):
        from django.db import IntegrityError
        app = ApplicationFactory()
        with pytest.raises(IntegrityError):
            ApplicationFactory(candidate=app.candidate, job=app.job)
