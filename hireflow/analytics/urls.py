from django.urls import path
from .views import PipelineStatsView, JobStatsView, RecruitingFunnelView, CandidateSourceView

urlpatterns = [
    path('analytics/pipeline/', PipelineStatsView.as_view(), name='analytics-pipeline'),
    path('analytics/jobs/', JobStatsView.as_view(), name='analytics-jobs'),
    path('analytics/funnel/', RecruitingFunnelView.as_view(), name='analytics-funnel'),
    path('analytics/candidates/', CandidateSourceView.as_view(), name='analytics-candidates'),
]
