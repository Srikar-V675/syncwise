from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    dept_name = models.CharField(max_length=50)

    def __str__(self):
        return self.dept_name


class User(AbstractUser):
    # TODO: make sure the null=True fields are correct.
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True
    )  # null=True because department is not known at the time of user creation for superuser.


class Batch(models.Model):
    dept = models.ForeignKey(Department, on_delete=models.CASCADE)
    batch_name = models.CharField(max_length=50)
    scheme = models.IntegerField(
        null=True
    )  # I'm still unsure if scheme is known at the time of batch creation
    num_students = models.IntegerField(
        default=0
    )  # defaulted to 0 cause if the number of students is not known, it can be updated later
    batch_start_year = models.IntegerField()
    batch_end_year = models.IntegerField()

    def __str__(self):
        return self.batch_name

    def count_num_students(self):
        # This method will be called when the number of students in the batch is to be updated
        # It will count the number of students in the batch and update the num_students field
        pass


class BatchAdmin(admin.ModelAdmin):
    list_display = (
        "batch_name",
        "dept",
        "scheme",
        "num_students",
        "batch_start_year",
        "batch_end_year",
    )


class Section(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    # assign class teacher to the section. one teacher can be assigned to multiple sections
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    section_name = models.CharField(max_length=1)  # A, B, C, etc.
    num_students = models.IntegerField(
        default=0
    )  # defaulted to 0 cause if the number of students is not known, it can be updated later

    def __str__(self):
        return self.section_name

    def count_num_students(self):
        # This method will be called when the number of students in the section is to be updated
        # It will count the number of students in the section and update the num_students field
        pass


class SectionAdmin(admin.ModelAdmin):
    list_display = ("batch", "section_name", "teacher", "num_students")


class Semester(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    sem_number = models.IntegerField()
    num_subjects = models.IntegerField(
        default=0
    )  # defaulted to 0 cause if the number of subjects is not known, it can be updated later
    current = models.BooleanField(default=False)

    def __str__(self):
        return f"Semester {self.sem_number}"

    def count_num_subjects(self):
        # This method will be called when the number of subjects in the semester is to be updated
        # It will count the number of subjects in the semester and update the num_subjects field
        pass


class SemesterAdmin(admin.ModelAdmin):
    list_display = ("batch", "sem_number", "num_subjects", "current")


class Subject(models.Model):
    sem = models.ForeignKey(Semester, on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=100)
    sub_code = models.CharField(max_length=10)
    credits = models.IntegerField()

    def __str__(self):
        return self.sub_name


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    semester = models.ForeignKey(
        Semester, on_delete=models.CASCADE
    )  # to indicate the current semester of the student
    usn = models.CharField(max_length=10, default="-", null=True)
    cgpa = models.FloatField(default=0.0)
    active = models.BooleanField(default=True)
    num_backlogs = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

    def count_num_backlogs(self):
        # This method will be called when the number of backlogs of the student is to be updated
        # It will count the number of backlogs of the student and update the num_backlogs field
        pass


class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "usn",
        "batch",
        "section",
        "semester",
        "cgpa",
        "active",
        "num_backlogs",
    )


# Faculty model is not yet implemented. I'm unsure if it is needed or not.
class Faculty(models.Model):
    pass


class Score(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    marks = models.JSONField()

    def __str__(self):
        return self.student.user.username + " - " + self.semester.sem_number

    def calculate_grade(self):
        # This method will be called when the grade of the student in the subject is to be calculated
        # It will calculate the grade of the student in the subject and update the grade field
        pass

    def calculate_cgpa(self):
        # This method will be called when the cgpa of the student is to be calculated
        # It will calculate the cgpa of the student and update the cgpa field
        pass

    def calculate_sgpa(self):
        # This method will be called when the sgpa of the student is to be calculated
        # It will calculate the sgpa of the student and update the sgpa field
        pass

    def calculate_percentage(self):
        # This method will be called when the percentage of the student is to be calculated
        # It will calculate the percentage of the student and update the percentage field
        pass

    def calculate_result(self):
        # This method will be called when the result of the student is to be calculated
        # It will calculate the result of the student and update the result field
        pass


class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    total = models.IntegerField()
    percentage = models.FloatField()
    sgpa = models.FloatField()
    # add more fields if needed based on info in dashboards

    def __str__(self):
        return self.student.user.username + " - " + self.semester.sem_number

    def calculate_sgpa(self):
        # This method will be called when the sgpa of the student is to be calculated
        # It will calculate the sgpa of the student and update the sgpa field
        pass

    def calculate_percentage(self):
        # This method will be called when the percentage of the student is to be calculated
        # It will calculate the percentage of the student and update the percentage field
        pass

    def calculate_result(self):
        # This method will be called when the result of the student is to be calculated
        # It will calculate the result of the student and update the result field
        pass
