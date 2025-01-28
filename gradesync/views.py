from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.redis_conn import get_scraping_info

from .filters import (
    BatchFilter,
    ScoreFilter,
    SectionFilter,
    SemesterFilter,
    SemesterMetricsFilter,
    StudentFilter,
    StudentPerformanceFilter,
    SubjectFilter,
    SubjectMetricsFilter,
)
from .models import (
    Batch,
    Department,
    Score,
    Section,
    Semester,
    SemesterMetrics,
    Student,
    StudentPerformance,
    Subject,
    SubjectMetrics,
    User,
)
from .serializers import (
    BatchSerializer,
    BatchSubjectSerializer,
    DepartmentSerializer,
    IdentifySubjectsSerializer,
    ScoreSerializer,
    ScrapeBatchSerializer,
    SectionSerializer,
    SemesterMetricsSerializer,
    SemesterSerializer,
    StudentBulkUploadSeializer,
    StudentPerformanceSerializer,
    StudentSerializer,
    SubjectMetricsSerializer,
    SubjectSerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(department=user.department)


class StudentViewSet(viewsets.ModelViewSet):
    serializer_class = StudentSerializer
    # queryset = Student.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter

    search_fields = ["batch__batch_name"]
    ordering_fields = ["usn", "cgpa", "num_backlogs"]
    ordering = ["usn"]

    def get_queryset(self):
        teacher = self.request.user
        sections = Section.objects.filter(teacher=teacher)
        return Student.objects.filter(section__in=sections)


# subject metric related view
# class SubjectMetricsListView(ListAPIView):
#     queryset = SubjectMetrics.objects.select_related('highest_scorer', 'section', 'subject', 'semester')
#     serializer_class = SubjectMetricsSerializer


class IdentifySubjectsView(APIView):
    serializer_class = IdentifySubjectsSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
        )

        if serializer.is_valid():
            subjects = serializer.save()

            return Response(
                subjects,
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ScrapeBatchView(APIView):
    serializer_class = ScrapeBatchSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
        )

        if serializer.is_valid():
            return Response(
                serializer.save(),
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FetchScrapingProgressView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        redis_name = kwargs.get("redis_name")

        if not redis_name:
            return Response(
                {"error": "Redis hash name not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        details = get_scraping_info(name=redis_name)

        if not details:
            return Response(
                {"error": "No scraping details found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response({"details": details})


class StudentBulkUploadView(APIView):
    serializer_class = StudentBulkUploadSeializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "message": "Students uploaded successfully",
                },
                status=status.HTTP_200_OK,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubjectFilter

    search_fields = ["subject_name", "subject_code"]
    ordering_fields = ["subject_code", "credits"]
    ordering = ["subject_code"]

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = BatchSubjectSerializer(data=request.data, many=True)
        else:
            serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SectionViewSet(viewsets.ModelViewSet):
    serializer_class = SectionSerializer
    queryset = Section.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SectionFilter

    search_fields = ["section_name"]
    ordering_fields = ["section_name"]
    ordering = ["section_name"]


class SemesterViewSet(viewsets.ModelViewSet):
    serializer_class = SemesterSerializer
    queryset = Semester.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SemesterFilter

    search_fields = ["semester_number"]
    ordering_fields = ["semester_number"]
    ordering = ["semester_number"]


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [IsAuthenticated]


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    queryset = Batch.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = BatchFilter

    search_fields = ["batch_name"]
    ordering_fields = ["scheme", "batch_start_year"]
    ordering = ["batch_start_year"]


class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    queryset = Score.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ScoreFilter

    search_fields = ["student__usn", "subject__subject_code"]
    ordering_fields = ["student__usn", "subject__subject_code"]
    ordering = ["student__usn"]


class StudentPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentPerformanceSerializer
    queryset = StudentPerformance.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentPerformanceFilter

    search_fields = ["student__usn", "semester__semester_number"]
    ordering_fields = [
        "student__usn",
        "semester__semester_number",
        "sgpa",
        "total",
        "percentage",
        "num_backlogs",
    ]
    ordering = ["student__usn"]


class SubjectMetricsViewSet(viewsets.ModelViewSet):
    serializer_class = SubjectMetricsSerializer
    queryset = SubjectMetrics.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SubjectMetricsFilter

    search_fields = [
        "section__section_name",
        "subject__subject_name",
        "semester__semester_number",
        "subject__subject_code",
    ]
    ordering_fields = [
        "section__section_name",
        "subject__subject_name",
        "semester__semester_number",
        "avg_score",
        "num_backlogs",
        "pass_percentage",
        "fail_percentage",
        "absent_percentage",
        "highest_scorer__usn",
        "highest_score",
    ]
    ordering = ["section__section_name"]


class SemesterMetricsViewSet(viewsets.ModelViewSet):
    serializer_class = SemesterMetricsSerializer
    queryset = SemesterMetrics.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SemesterMetricsFilter

    search_fields = ["section__section_name", "semester__semester_number"]
    ordering_fields = [
        "section__section_name",
        "semester__semester_number",
        "avg_score",
        "num_backlogs",
        "pass_percentage",
        "fail_percentage",
        "fail_1_sub",
        "fail_2_subs",
        "fail_3_subs",
        "fail_greater_3_subs",
    ]
    ordering = ["section__section_name"]
