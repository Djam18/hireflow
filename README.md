# Hireflow

An ATS (Applicant Tracking System) to manage job postings and candidate applications.

## Features

- Job posting management (CRUD)
- Candidate application tracking
- Pipeline stages: Applied → Screen → Interview → Offer → Hired / Rejected
- Multi-user with roles: Admin, Recruiter, Viewer
- File upload for resumes

## Setup

```
pip install -r requirements.txt
cp .env.example .env
# edit .env with your values
python manage.py migrate
python manage.py runserver
```
