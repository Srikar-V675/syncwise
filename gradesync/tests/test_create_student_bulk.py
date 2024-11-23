import pandas as pd
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Batch, Department, Section, Semester, Student, User


class CreateStudentBulkTests(APITestCase):
    def setUp(self):
        call_command("create_groups")
        self.user = User.objects.create_user(username="test-teacher", password="test")
        self.user.groups.add(Group.objects.get(name="Teachers"))
        self.department = Department.objects.create(dept_name="Test Department")
        self.batch = Batch.objects.create(
            dept=self.department,
            batch_name="Test Batch",
            batch_start_year=2020,
            batch_end_year=2024,
        )
        self.semester = Semester.objects.create(
            batch=self.batch, sem_number=1, current=True
        )
        self.section = Section.objects.create(
            section_name="A", batch=self.batch, teacher=self.user
        )
        url = reverse("token_obtain_pair")
        data = {"username": "test-teacher", "password": "test"}
        response = self.client.post(url, data, format="json")
        self.access_token = response.data["access"]
        # create a csv file with student data
        self.csv_data = pd.DataFrame(
            {
                "first_name": ["Test1", "Test2"],
                "last_name": ["Student1", "Student2"],
                "email": ["test1@example.com", "test2.example.com"],
            }
        )
        self.csv_file = ContentFile(
            self.csv_data.to_csv(index=False), name="students.csv"
        )

    def test_create_student_bulk(self):
        """
        Ensure we can create students in bulk
        """
        url = "/api/upload/"
        data = {
            "file": self.csv_file,
            "batch": self.batch.id,
            "section": self.section.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Students uploaded successfully")

        self.assertEqual(Student.objects.count(), 2)

    def test_create_student_bulk_invalid_file(self):
        """
        Ensure we can't create students with invalid file
        """
        url = "/api/upload/"
        data = {
            "file": ContentFile(b"invalid file", name="invalid.csv"),
            "batch": self.batch.id,
            "section": self.section.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Student.objects.count(), 0)

    def test_create_student_bulk_invalid_file_type(self):
        """
        Ensure we can't create students with invalid file type
        """
        url = "/api/upload/"
        data = {
            "file": ContentFile(b"invalid file", name="invalid.txt"),
            "batch": self.batch.id,
            "section": self.section.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Student.objects.count(), 0)

    def test_create_student_bulk_invalid_batch(self):
        """
        Ensure we can't create students with invalid batch
        """
        url = "/api/upload/"
        data = {
            "file": self.csv_file,
            "batch": 999,
            "section": self.section.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("batch", response.data)
        self.assertEqual(Student.objects.count(), 0)

    def test_create_student_bulk_invalid_section(self):
        """
        Ensure we can't create students with invalid section
        """
        url = "/api/upload/"
        data = {
            "file": self.csv_file,
            "batch": self.batch.id,
            "section": 999,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("section", response.data)
        self.assertEqual(Student.objects.count(), 0)

    def test_create_student_bulk_invalid_semester(self):
        """
        Ensure we can't create students with invalid semester
        """
        url = "/api/upload/"
        data = {
            "file": self.csv_file,
            "batch": self.batch.id,
            "section": self.section.id,
            "semester": 999,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION=f"Bearer {self.access_token}",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("semester", response.data)
        self.assertEqual(Student.objects.count(), 0)

    def test_create_student_bulk_invalid_teacher(self):
        """
        Ensure we can't create students with invalid teacher
        """
        url = "/api/upload/"
        data = {
            "file": self.csv_file,
            "batch": self.batch.id,
            "section": self.section.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            HTTP_AUTHORIZATION="Bearer invalid-token",
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Student.objects.count(), 0)
