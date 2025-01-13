import json
import threading

import pandas as pd
from django.contrib.auth.models import Group
from rest_framework import serializers

from utils.driver import initialise_driver
from utils.redis_conn import init_scraping_redis_key
from utils.scraper import check_url, scrape_result, status_code_str
from utils.scraper_drf import scrape_bg_task

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name")

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


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = "__all__"


class StudentPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPerformance
        fields = "__all__"


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"


class SubjectListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        # perform batch operation
        return Subject.objects.bulk_create([Subject(**item) for item in validated_data])

    # TODO: Implement below method in future
    def update(self, validated_data):
        pass


class BatchSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"
        list_serializer_class = SubjectListSerializer


class IdentifySubjectsSerializer(serializers.Serializer):
    usn = serializers.CharField(max_length=10, allow_blank=False)
    result_url = serializers.URLField(allow_blank=False)

    def create(self, validated_data):
        try:
            usn = validated_data["usn"]
            result_url = str(validated_data["result_url"])

            check_url(url=result_url)

            driver = initialise_driver()
            scraped_res = scrape_result(USN=usn, url=result_url, driver=driver)

            subjects = [
                {"sub_name": mark["Subject Name"], "sub_code": mark["Subject Code"]}
                for mark in json.loads(scraped_res[0])["Marks"]  # type: ignore
            ]
            code = status_code_str(code=scraped_res[1])

            return {"subjects": subjects, "status": code}
        except Exception as e:
            return {"error": e}


class ScrapeBatchSerializer(serializers.Serializer):
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())
    result_url = serializers.URLField(allow_blank=False)

    def create(self, validated_data):
        try:
            batch = validated_data["batch"]
            semester = validated_data["semester"]
            result_url = str(validated_data["result_url"])

            check_url(url=result_url)

            students = Student.objects.filter(batch=batch)

            redis_name = init_scraping_redis_key(total=len(students))

            thread = threading.Thread(
                target=scrape_bg_task,
                args=(
                    semester,
                    students,
                    redis_name,
                    result_url,
                ),
            )
            thread.start()

            return {
                "message": "Scraping background task has started.",
                "redis_name": redis_name,
            }
        except Exception as e:
            return {"error": str(e)}


# TODO: create an endpoint for batch upadting the student performance
class BatchComputePerformanceSerializer(serializers.Serializer):
    batch = serializers.PrimaryKeyRelatedField(queryset=Batch.objects.all())
    semester = serializers.PrimaryKeyRelatedField(queryset=Semester.objects.all())

    def create(self, validated_data):
        try:
            # batch = validated_data['batch']
            semester = validated_data["semester"]

            scores = Score.objects.filter(semester=semester)
            performances = []

            for score in scores:
                total = score.calculate_total()
                percentage = score.calculate_percentage(total=total)
                sgpa = score.calculate_sgpa()

                performances.append(
                    StudentPerformance(
                        student=score.student,
                        semester=score.semester,
                        total=total,
                        percentage=percentage,
                        sgpa=sgpa,
                    )
                )
            StudentPerformance.objects.bulk_create(performances)

            return {
                "message": "Succesfully computed student performances",
            }
        except Exception as e:
            return {"error": str(e)}


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
