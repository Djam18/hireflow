import pytest
from rest_framework.test import APIClient
from .factories import UserFactory, AdminUserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def recruiter_user(db):
    return UserFactory()


@pytest.fixture
def admin_user(db):
    return AdminUserFactory()


@pytest.fixture
def auth_client(db):
    client = APIClient()
    user = UserFactory()
    client.force_authenticate(user=user)
    return client, user


@pytest.fixture
def admin_client(db):
    client = APIClient()
    user = AdminUserFactory()
    client.force_authenticate(user=user)
    return client, user
