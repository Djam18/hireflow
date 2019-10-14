import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from accounts.models import CustomUser
from jobs.models import Job
from candidates.models import Candidate
from pipeline.models import Application

User = get_user_model()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = CustomUser.Role.RECRUITER
    is_active = True


class AdminUserFactory(UserFactory):
    role = CustomUser.Role.ADMIN
    is_staff = True
    is_superuser = True


class JobFactory(DjangoModelFactory):
    class Meta:
        model = Job

    title = factory.Sequence(lambda n: f'Software Engineer {n}')
    description = factory.Faker('paragraph')
    location = factory.Faker('city')
    job_type = Job.JobType.FULL_TIME
    salary_min = 50000
    salary_max = 80000
    is_active = True
    posted_by = factory.SubFactory(UserFactory)


class CandidateFactory(DjangoModelFactory):
    class Meta:
        model = Candidate

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Sequence(lambda n: f'candidate{n}@example.com')
    phone = factory.Faker('phone_number')


class ApplicationFactory(DjangoModelFactory):
    class Meta:
        model = Application

    candidate = factory.SubFactory(CandidateFactory)
    job = factory.SubFactory(JobFactory)
    stage = Application.Stage.NEW
