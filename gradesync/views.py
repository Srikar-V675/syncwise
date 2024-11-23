from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Batch, Department, Section, Semester, Student, User
from .serializers import (
    BatchSerializer,
    DepartmentSerializer,
    SectionSerializer,
    SemesterSerializer,
    StudentBulkUploadSeializer,
    StudentSerializer,
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
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
