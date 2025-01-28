from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from gradesync.views import (
    BatchViewSet,
    DepartmentViewSet,
    FetchScrapingProgressView,
    IdentifySubjectsView,
    ScoreViewSet,
    ScrapeBatchView,
    SectionViewSet,
    SemesterMetricsViewSet,
    SemesterViewSet,
    StudentBulkUploadView,
    StudentPerformanceViewSet,
    StudentViewSet,
    SubjectMetricsViewSet,
    SubjectViewSet,
    UserViewSet,
)

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"students", StudentViewSet, basename="student")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"batches", BatchViewSet, basename="batch")
router.register(r"sections", SectionViewSet, basename="section")
router.register(r"semesters", SemesterViewSet, basename="semester")
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"scores", ScoreViewSet, basename="score")
router.register(
    r"student-performances", StudentPerformanceViewSet, basename="student-performance"
)
router.register(r"subject-metrics", SubjectMetricsViewSet, basename="subject-metrics")
router.register(
    r"semester-metrics", SemesterMetricsViewSet, basename="semester-metrics"
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/", include(router.urls)),  # Include the router's URLs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
    path("api/upload/", StudentBulkUploadView.as_view(), name="student-upload"),
    path("api/identify/", IdentifySubjectsView.as_view(), name="identify-subjects"),
    path("api/scrape/batch/", ScrapeBatchView.as_view(), name="scrape-batch"),
    path(
        "api/scrape/progress/<str:redis_name>/",
        FetchScrapingProgressView.as_view(),
        name="scraping-progress",
    ),
]
