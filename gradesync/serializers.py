import pandas as pd
from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import Batch, Department, Section, Semester, Student, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "password", "first_name", "last_name")

    def create(self, validated_data):
        # assign group to user
        user = super().create(validated_data)
        group = Group.objects.get(name="Students")
        user.groups.add(group)

        teacher = self.context["request"].user
        user.department = teacher.department

        user.set_password(validated_data["password"])
        user.save()
        return user


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = "__all__"


class SemesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Semester
        fields = "__all__"


class StudentBulkUploadSeializer(serializers.Serializer):
    file = serializers.FileField()
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())
    section = serializers.PrimaryKeyRelatedField(queryset=Section.objects.all())
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())

    def create(self, validated_data):
        # TODO: add validation for the file
        # TODO: send statistics of success and failure of student creation
        # TODO: add logging
        batch = validated_data["batch"]
        section = validated_data["section"]
        semester = validated_data["semester"]
        teacher = self.context["request"].user
        department = teacher.department

        uploaded_file = validated_data["file"]
        # check if the file is csv
        if not uploaded_file.name.endswith(".csv"):
            raise serializers.ValidationError("Invalid file type")

        # read the file and create students
        df = pd.read_csv(uploaded_file)

        users = []
        students = []

        try:
            for _, row in df.iterrows():
                # validate the data
                if not row["email"]:
                    raise serializers.ValidationError("Email is required")
                if not row["first_name"]:
                    raise serializers.ValidationError("First name is required")
                if not row["last_name"]:
                    raise serializers.ValidationError("Last name is required")
                user = User(
                    username=row["email"],
                    email=row["email"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    department=department,
                )
                user.set_password(row["email"])
                users.append(user)

                student = Student(
                    user=user,
                    batch=batch,
                    section=section,
                    semester=semester,
                )
                students.append(student)
        except Exception as e:
            raise serializers.ValidationError(str(e))

        if not users:
            raise serializers.ValidationError("No valid data found in the file")
        User.objects.bulk_create(users)
        # add group to users
        group = Group.objects.get(name="Students")
        for user in users:
            user.groups.add(group)
        if not students:
            raise serializers.ValidationError("No valid data found in the file")
        Student.objects.bulk_create(students)

        return students
