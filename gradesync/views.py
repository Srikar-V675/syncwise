from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.redis_conn import get_scraping_info

from .models import (
    Batch,
    Department,
    Score,
    Section,
    Semester,
    Student,
    StudentPerformance,
    Subject,
    User,
)
from .serializers import (
    BatchComputePerformanceSerializer,
    BatchSerializer,
    BatchSubjectSerializer,
    DepartmentSerializer,
    IdentifySubjectsSerializer,
    ScoreSerializer,
    ScrapeBatchSerializer,
    SectionSerializer,
    SemesterSerializer,
    StudentBulkUploadSeializer,
    StudentPerformanceSerializer,
    StudentSerializer,
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

    def get_queryset(self):
        teacher = self.request.user
        sections = Section.objects.filter(teacher=teacher)
        return Student.objects.filter(section__in=sections)


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


class BatchComputePerformanceView(APIView):
    serializer_class = BatchComputePerformanceSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serialzer = self.serializer_class(data=request.data)

        if serialzer.is_valid():
            return Response(serialzer.save(), status=status.HTTP_200_OK)

        return Response(serialzer.errors, status=status.HTTP_400_BAD_REQUEST)


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


class SemesterViewSet(viewsets.ModelViewSet):
    serializer_class = SemesterSerializer
    queryset = Semester.objects.all()
    permission_classes = [IsAuthenticated]


class DepartmentViewSet(viewsets.ModelViewSet):
    serializer_class = DepartmentSerializer
    queryset = Department.objects.all()
    permission_classes = [IsAuthenticated]


class BatchViewSet(viewsets.ModelViewSet):
    serializer_class = BatchSerializer
    queryset = Batch.objects.all()
    permission_classes = [IsAuthenticated]


class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = ScoreSerializer
    queryset = Score.objects.all()
    permission_classes = [IsAuthenticated]


class StudentPerformanceViewSet(viewsets.ModelViewSet):
    serializer_class = StudentPerformanceSerializer
    queryset = StudentPerformance.objects.all()
    permission_classes = [IsAuthenticated]
