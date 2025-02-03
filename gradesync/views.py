from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import api_view
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
    queryset = Student.objects.all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = StudentFilter

    search_fields = ["batch__batch_name"]
    ordering_fields = ["usn", "cgpa", "num_backlogs"]
    ordering = ["usn"]


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


@api_view(["GET"])
def get_scores_by_section_and_semester(request, section_id, semester_id):
    section = Section.objects.filter(id=section_id).first()
    semester = Semester.objects.filter(id=semester_id).first()

    if not section or not semester:
        return Response(
            {"error": "Section or Semester does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    students = Student.objects.filter(section=section_id, active=True).prefetch_related(
        Prefetch(
            "score_set",
            queryset=Score.objects.filter(semester=semester_id),
            to_attr="cached_scores",
        ),
        Prefetch(
            "studentperformance_set",
            queryset=StudentPerformance.objects.filter(semester=semester_id),
            to_attr="cached_performance",
        ),
    )

    student_data = []
    for student in students:
        student_info = {
            "id": student.id,
            "usn": student.usn,
            "name": student.user.first_name,
            "total": student.cached_performance[0].total,
            "sgpa": student.cached_performance[0].sgpa,
            "percentage": student.cached_performance[0].percentage,
            "scores": [
                {
                    "id": score.id,
                    "subject_name": score.subject.sub_name,
                    "subject_code": score.subject.sub_code,
                    "internal": score.internal,
                    "external": score.external,
                    "total": score.total,
                    "grade": score.grade,
                }
                for score in student.cached_scores
            ],
        }

        student_data.append(student_info)

    return Response(student_data)


@api_view(["GET"])
def get_scores_by_student(request, student_id):
    student = Student.objects.filter(id=student_id).first()

    if not student:
        return Response(
            {"error": "Student does not exist"},
            status=status.HTTP_404_NOT_FOUND,
        )

    semesters = Semester.objects.filter(batch=student.batch).prefetch_related(
        Prefetch(
            "score_set",
            queryset=Score.objects.filter(student=student_id),
            to_attr="cached_scores",
        ),
        Prefetch(
            "studentperformance_set",
            queryset=StudentPerformance.objects.filter(student=student_id),
            to_attr="cached_performance",
        ),
    )

    student_data = []
    for semester in semesters:
        student_info = {
            "semester": semester.semester_number,
            "total": semester.cached_performance[0].total,
            "sgpa": semester.cached_performance[0].sgpa,
            "percentage": semester.cached_performance[0].percentage,
            "scores": [
                {
                    "id": score.id,
                    "subject_name": score.subject.sub_name,
                    "subject_code": score.subject.sub_code,
                    "internal": score.internal,
                    "external": score.external,
                    "total": score.total,
                    "grade": score.grade,
                }
                for score in semester.cached_scores
            ],
        }

        student_data.append(student_info)

    return Response(student_data)


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
    ordering = ["section__section_name"]

    def get_queryset(self):
        return SubjectMetrics.objects.select_related(
            "subject", "highest_scorer", "highest_scorer__user"
        )


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
