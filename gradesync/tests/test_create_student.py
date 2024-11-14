from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Batch, Department, Section, Semester, User


class CreateStudentTests(APITestCase):
    # TODO: test creating student with invalid user
    def setUp(self):
        """
        Create test records to test creating a student
        """
        call_command("create_groups")
        self.user1 = User.objects.create_user(username="test-teacher1", password="test")
        self.user1.groups.add(Group.objects.get(name="Teachers"))
        self.user2 = User.objects.create_user(username="test-teacher2", password="test")
        self.user2.groups.add(Group.objects.get(name="Teachers"))
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
        self.section1 = Section.objects.create(
            section_name="A", batch=self.batch, teacher=self.user1
        )
        self.section2 = Section.objects.create(
            section_name="B", batch=self.batch, teacher=self.user2
        )
        # get access tokens for the teachers
        url = reverse("token_obtain_pair")
        data = {"username": "test-teacher1", "password": "test"}
        response = self.client.post(url, data, format="json")
        self.teacher1_access_token = response.data["access"]
        data = {"username": "test-teacher2", "password": "test"}
        response = self.client.post(url, data, format="json")
        self.teacher2_access_token = response.data["access"]

    def test_create_get_student_user(self):
        """
        Ensure we can create a student user
        """
        url = "/api/users/"
        data = {
            "username": "test-student1",
            "email": "test-student1@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "Student1",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/api/users/" + f"{response.data['id']}/"
        response = self.client.get(
            url, HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_get_student(self):
        """
        Ensure we can create a student
        """
        url = "/api/users/"
        data = {
            "username": "test-student1",
            "email": "test-student1@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "Student1",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )

        url = "/api/students/"
        data = {
            "user": response.data["id"],
            "batch": self.batch.id,
            "section": self.section1.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/api/students/" + f"{response.data['id']}/"
        response = self.client.get(
            url, HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_get_class_teacher_student_invalid(self):
        """
        Ensure we can get a student
        """
        url = "/api/users/"
        data = {
            "username": "test-student1",
            "email": "test-student1@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "Student1",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )

        url = "/api/students/"
        data = {
            "user": response.data["id"],
            "batch": self.batch.id,
            "section": self.section1.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = "/api/students/" + f"{response.data['id']}/"
        response = self.client.get(
            url, HTTP_AUTHORIZATION=f"Bearer {self.teacher2_access_token}"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_student_invalid_section(self):
        """
        Ensure we can't create a student with invalid section
        """
        url = "/api/users/"
        data = {
            "username": "test-student1",
            "email": "test-student1@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "Student1",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )

        url = "/api/students/"
        data = {
            "user": response.data["id"],
            "batch": self.batch.id,
            "section": 999,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_student_invalid_semester(self):
        """
        Ensure we can't create a student with invalid semester
        """
        url = "/api/users/"
        data = {
            "username": "test-student1",
            "email": "test-student1@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "Student1",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )

        url = "/api/students/"
        data = {
            "user": response.data["id"],
            "batch": self.batch.id,
            "section": self.section1.id,
            "semester": 999,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_student_invalid_batch(self):
        """
        Ensure we can't create a student with invalid batch
        """
        url = "/api/users/"
        data = {
            "username": "test-student1",
            "email": "test-student1@example.com",
            "password": "test",
            "first_name": "Test",
            "last_name": "Student1",
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )

        url = "/api/students/"
        data = {
            "user": response.data["id"],
            "batch": 999,
            "section": self.section1.id,
            "semester": self.semester.id,
        }
        response = self.client.post(
            url,
            data,
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {self.teacher1_access_token}",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
