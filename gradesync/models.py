from django.contrib import admin
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Avg, Prefetch, Sum


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
        # It will count the number of students in the batch and update the num_students field
        total_students = Section.objects.filter(batch=self).aggregate(
            total=Sum("num_students")
        )["total"]
        self.num_students = total_students or 0
        self.save()


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
        # It will count the number of students in the section and update the num_students field
        self.num_students = Student.objects.filter(section=self, active=True).count()
        self.save()


class SectionAdmin(admin.ModelAdmin):
    list_display = ("batch", "section_name", "teacher", "num_students")


class Semester(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    semester_number = models.IntegerField()
    num_subjects = models.IntegerField(
        default=0
    )  # defaulted to 0 cause if the number of subjects is not known, it can be updated later
    current = models.BooleanField(default=False)

    def __str__(self):
        return f"Semester {self.semester_number}"

    def count_num_subjects(self):
        # It will count the number of subjects in the semester and update the num_subjects field
        self.num_subjects = Subject.objects.filter(semester=self).count()
        self.save()


class SemesterAdmin(admin.ModelAdmin):
    list_display = ("batch", "semester_number", "num_subjects", "current")


class Subject(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    sub_name = models.CharField(max_length=100)
    sub_code = models.CharField(max_length=10)
    credits = models.IntegerField()

    def __str__(self):
        return self.sub_name


class SubjectAdmin(admin.ModelAdmin):
    list_display = ("semester", "sub_name", "sub_code", "credits")


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

    def calculate_cgpa(self):
        cgpa = StudentPerformance.objects.filter(student=self).aggregate(
            average=Avg("sgpa")
        )["average"]
        self.cgpa = cgpa or 0.0
        self.save()

    def count_num_backlogs(self):
        # It will count the number of backlogs of the student and update the num_backlogs field
        # grade Fail or Absent is considered as backlog
        self.num_backlogs = StudentPerformance.objects.filter(
            student=self, num_backlogs__gt=0
        ).count()
        self.save()


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
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    internal = models.IntegerField()
    external = models.IntegerField()
    total = models.IntegerField()
    grade = models.CharField(max_length=3)

    def __str__(self):
        return (
            self.student.user.username
            + " - "
            + str(self.semester.semester_number)
            + " - "
            + self.subject.sub_name
        )


class ScoreAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "semester",
        "subject",
        "internal",
        "external",
        "total",
        "grade",
    )


class SubjectMetrics(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    avg_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    num_backlogs = models.IntegerField(default=0)
    pass_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fail_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    absent_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fcd_count = models.IntegerField(default=0)
    fc_count = models.IntegerField(default=0)
    sc_count = models.IntegerField(default=0)
    fail_count = models.IntegerField(default=0)
    absent_count = models.IntegerField(default=0)
    highest_score = models.IntegerField(default=0)
    highest_scorer = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="highest_scorer",
    )

    def __str__(self):
        return (
            self.section.section_name
            + " - "
            + self.subject.sub_name
            + " - "
            + str(self.semester.semester_number)
        )

    def _calculate_counts(self, scores):
        (
            total_score,
            num_backlogs,
            fcd_count,
            fc_count,
            sc_count,
            fail_count,
            absent_count,
            highest_score,
        ) = (0, 0, 0, 0, 0, 0, 0, 0)
        highest_scorer = None

        for score in scores:
            total_score += score.total
            if score.total > highest_score:
                highest_score = score.total
                highest_scorer = score.student

            grade = score.grade
            if grade == "FCD":
                fcd_count += 1
            elif grade == "FC":
                fc_count += 1
            elif grade == "SC":
                sc_count += 1
            elif grade == "F":
                fail_count += 1
                num_backlogs += 1
            elif grade == "A":
                absent_count += 1
                num_backlogs += 1

        return (
            total_score,
            num_backlogs,
            fcd_count,
            fc_count,
            sc_count,
            fail_count,
            absent_count,
            highest_score,
            highest_scorer,
        )

    def _update_metrics(
        self,
        total_students,
        total_score,
        num_backlogs,
        fcd_count,
        fc_count,
        sc_count,
        fail_count,
        absent_count,
        highest_score,
        highest_scorer,
    ):
        self.num_backlogs = num_backlogs
        self.avg_score = (
            round(total_score / total_students, 2) if total_students > 0 else 0
        )
        self.pass_percentage = (
            round((fcd_count + fc_count + sc_count) / total_students * 100, 2)
            if total_students > 0
            else 0
        )
        self.fail_percentage = (
            round(fail_count / total_students * 100, 2) if total_students > 0 else 0
        )
        self.absent_percentage = (
            round(absent_count / total_students * 100, 2) if total_students > 0 else 0
        )
        self.fcd_count = fcd_count
        self.fc_count = fc_count
        self.sc_count = sc_count
        self.fail_count = fail_count
        self.absent_count = absent_count
        self.highest_score = highest_score
        self.highest_scorer = highest_scorer

        self.save()

    def calculate_metrics(self):
        scores = Score.objects.filter(
            subject=self.subject, semester=self.semester, student__section=self.section
        )

        total_students = self.section.num_students
        if total_students == 0:
            return

        (
            total_score,
            num_backlogs,
            fcd_count,
            fc_count,
            sc_count,
            fail_count,
            absent_count,
            highest_score,
            highest_scorer,
        ) = self._calculate_counts(scores=scores)

        self._update_metrics(
            total_students=total_students,
            total_score=total_score,
            num_backlogs=num_backlogs,
            fcd_count=fcd_count,
            fc_count=fc_count,
            sc_count=sc_count,
            fail_count=fail_count,
            absent_count=absent_count,
            highest_score=highest_score,
            highest_scorer=highest_scorer,
        )


class SubjectMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "section",
        "subject",
        "semester",
        "avg_score",
        "num_backlogs",
        "pass_percentage",
        "fail_percentage",
        "absent_percentage",
        "fcd_count",
        "fc_count",
        "sc_count",
        "fail_count",
        "absent_count",
        "highest_score",
        "highest_scorer",
    )


class SemesterMetrics(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    avg_sgpa = models.DecimalField(
        max_digits=4, decimal_places=2, default=0
    )  # average sgpa of the section
    total_backlogs = models.IntegerField(
        default=0
    )  # total number of students with backlogs
    pass_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )  # total number of students that didn't have backlogs
    fail_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )  # total number of students with backlogs
    pass_count = models.IntegerField(default=0)
    fail_1_sub = models.IntegerField(default=0)  # students with 1 backlog
    fail_2_subs = models.IntegerField(default=0)  # students with 2 backlogs
    fail_3_subs = models.IntegerField(default=0)  # students with 3 backlogs
    fail_greater_3_subs = models.IntegerField(
        default=0
    )  # students with more than 3 backlogs

    def __str__(self):
        return f"{self.semester.semester_number}" + " - " + self.section.section_name

    def _calculate_fails(self, scores):
        """Calculate the number of failed subjects for a given set of scores."""
        fail_count = 0
        for score in scores:
            if score.grade in ["F", "A"]:
                fail_count += 1
        return fail_count

    def _calculate_counts(
        self,
        fail_count,
        pass_count,
        total_backlogs,
        fail_1_sub,
        fail_2_subs,
        fail_3_subs,
        fail_greater_3_subs,
    ):
        """Update counts based on the number of failed subjects."""
        if fail_count == 0:
            pass_count += 1
        else:
            total_backlogs += 1
            if fail_count == 1:
                fail_1_sub += 1
            elif fail_count == 2:
                fail_2_subs += 1
            elif fail_count == 3:
                fail_3_subs += 1
            else:
                fail_greater_3_subs += 1

        return (
            pass_count,
            total_backlogs,
            fail_1_sub,
            fail_2_subs,
            fail_3_subs,
            fail_greater_3_subs,
        )

    def _update_metrics(
        self,
        total_students,
        total_sgpa,
        pass_count,
        total_backlogs,
        fail_1_sub,
        fail_2_subs,
        fail_3_subs,
        fail_greater_3_subs,
    ):
        """Update the metrics for the semester performance."""
        self.avg_sgpa = (
            round(total_sgpa / total_students, 2) if total_students > 0 else 0
        )
        self.pass_percentage = (
            round(pass_count / total_students * 100, 2) if total_students > 0 else 0
        )
        self.fail_percentage = (
            round(total_backlogs / total_students * 100, 2) if total_students > 0 else 0
        )
        self.pass_count = pass_count
        self.total_backlogs = total_backlogs
        self.fail_1_sub = fail_1_sub
        self.fail_2_subs = fail_2_subs
        self.fail_3_subs = fail_3_subs
        self.fail_greater_3_subs = fail_greater_3_subs

        self.save()

    def calculate_metrics(self):
        """Main function to calculate metrics for a given section and semester."""
        students = Student.objects.filter(section=self.section, active=True)
        total_students = students.count()

        if total_students == 0:
            return

        # Prefetch scores for the given semester for all students
        scores = Score.objects.filter(semester=self.semester)
        students = students.prefetch_related(
            Prefetch("score_set", queryset=scores, to_attr="cached_scores")
        )

        (
            total_sgpa,
            pass_count,
            total_backlogs,
            fail_1_sub,
            fail_2_subs,
            fail_3_subs,
            fail_greater_3_subs,
        ) = (0, 0, 0, 0, 0, 0, 0)

        for student in students:
            # Use prefetched scores instead of querying the database again
            student_scores = student.cached_scores

            fail_count = self._calculate_fails(student_scores)

            student_performance = StudentPerformance.objects.get(
                student=student, semester=self.semester
            )
            total_sgpa += student_performance.sgpa

            (
                pass_count,
                total_backlogs,
                fail_1_sub,
                fail_2_subs,
                fail_3_subs,
                fail_greater_3_subs,
            ) = self._calculate_counts(
                fail_count=fail_count,
                pass_count=pass_count,
                total_backlogs=total_backlogs,
                fail_1_sub=fail_1_sub,
                fail_2_subs=fail_2_subs,
                fail_3_subs=fail_3_subs,
                fail_greater_3_subs=fail_greater_3_subs,
            )

        self._update_metrics(
            total_students=total_students,
            total_sgpa=total_sgpa,
            pass_count=pass_count,
            total_backlogs=total_backlogs,
            fail_1_sub=fail_1_sub,
            fail_2_subs=fail_2_subs,
            fail_3_subs=fail_3_subs,
            fail_greater_3_subs=fail_greater_3_subs,
        )


class SemesterMetricsAdmin(admin.ModelAdmin):
    list_display = (
        "semester",
        "section",
        "avg_sgpa",
        "total_backlogs",
        "pass_percentage",
        "fail_percentage",
        "pass_count",
        "fail_1_sub",
        "fail_2_subs",
        "fail_3_subs",
        "fail_greater_3_subs",
    )


class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    total = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    sgpa = models.FloatField(default=0.0)
    num_backlogs = models.IntegerField(default=0)

    def __str__(self):
        return self.student.user.username + " - " + str(self.semester.semester_number)

    def _calculate_metrics(self, scores):
        """
        Loops through scores once to calculate:
        - Total marks
        - SGPA
        - Total credits
        - Number of backlogs
        """
        total = 0
        sgpa = 0
        total_credits = 0
        num_backlogs = 0

        for score in scores:
            total += score.total
            credits = score.subject.credits
            total_credits += credits

            # Calculate number of backlogs
            if score.grade in ["F", "A"]:
                num_backlogs += 1

            # Calculate SGPA component based on score ranges
            if score.total >= 90:
                sgpa += 10 * credits
            elif score.total >= 80:
                sgpa += 9 * credits
            elif score.total >= 70:
                sgpa += 8 * credits
            elif score.total >= 60:
                sgpa += 7 * credits
            elif score.total >= 50:
                sgpa += 6 * credits
            elif score.total >= 40:
                sgpa += 5 * credits
            else:
                sgpa += 0

        # Final SGPA calculation
        sgpa = round(sgpa / total_credits, 2) if total_credits > 0 else 0
        return total, sgpa, num_backlogs

    def _calculate_percentage(self, total):
        """
        Calculates percentage based on the total marks.
        """
        max_total = self.semester.num_subjects * 100
        return round((total / max_total) * 100, 2) if max_total > 0 else 0

    def calculate_all(self):
        """
        Calculates total marks, SGPA, and percentage in one pass through the scores.
        """
        scores = Score.objects.filter(student=self.student, semester=self.semester)

        # Calculate total, SGPA, and total credits in one loop
        total, sgpa, num_backlogs = self._calculate_metrics(scores)

        # Calculate percentage
        percentage = self._calculate_percentage(total)

        # Update fields
        self.total = total
        self.sgpa = sgpa
        self.percentage = percentage
        self.num_backlogs = num_backlogs
        self.save()


class StudentPerformanceAdmin(admin.ModelAdmin):
    list_display = ("student", "semester", "total", "percentage", "sgpa")
