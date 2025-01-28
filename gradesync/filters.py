import django_filters

from gradesync.models import (
    Batch,
    Score,
    Section,
    Semester,
    SemesterMetrics,
    Student,
    StudentPerformance,
    Subject,
    SubjectMetrics,
)


class BatchFilter(django_filters.FilterSet):
    class Meta:
        model = Batch
        fields = {
            "scheme": ["exact"],
            "num_students": ["exact", "lt", "gt"],
            "batch_start_year": ["exact", "lt", "gt"],
        }


class SectionFilter(django_filters.FilterSet):
    class Meta:
        model = Section
        fields = {
            "teacher": ["exact"],
            "batch": ["exact"],
            "num_students": ["exact", "lt", "gt"],
        }


class SemesterFilter(django_filters.FilterSet):
    class Meta:
        model = Semester
        fields = {
            "batch": ["exact"],
            "semester_number": ["exact", "lt", "gt"],
            "num_subjects": ["exact", "lt", "gt"],
            "current": ["exact"],
        }


class SubjectFilter(django_filters.FilterSet):
    class Meta:
        model = Subject
        fields = {
            "semester": ["exact"],
            "sub_code": ["exact"],
            "sub_name": ["exact"],
            "credits": ["exact", "lt", "gt"],
        }


class StudentFilter(django_filters.FilterSet):
    class Meta:
        model = Student
        fields = {
            "batch": ["exact"],
            "section": ["exact"],
            "usn": ["exact"],
            "cgpa": ["exact", "lt", "gt"],
            "active": ["exact"],
            "num_backlogs": ["exact", "lt", "gt"],
        }


class ScoreFilter(django_filters.FilterSet):
    class Meta:
        model = Score
        fields = {
            "student": ["exact"],
            "subject": ["exact"],
            "semester": ["exact"],
            "internal": ["exact", "lt", "gt"],
            "external": ["exact", "lt", "gt"],
            "total": ["exact", "lt", "gt"],
            "grade": ["exact"],
        }


class StudentPerformanceFilter(django_filters.FilterSet):
    class Meta:
        model = StudentPerformance
        fields = {
            "student": ["exact"],
            "semester": ["exact"],
            "total": ["exact", "lt", "gt"],
            "percentage": ["exact", "lt", "gt"],
            "sgpa": ["exact", "lt", "gt"],
            "num_backlogs": ["exact", "lt", "gt"],
        }


class SubjectMetricsFilter(django_filters.FilterSet):
    class Meta:
        model = SubjectMetrics
        fields = {
            "section": ["exact"],
            "subject": ["exact"],
            "semester": ["exact"],
            "avg_score": ["exact", "lt", "gt"],
            "num_backlogs": ["exact", "lt", "gt"],
            "pass_percentage": ["exact", "lt", "gt"],
            "fail_percentage": ["exact", "lt", "gt"],
            "absent_percentage": ["exact", "lt", "gt"],
            "fcd_count": ["exact", "lt", "gt"],
            "fc_count": ["exact", "lt", "gt"],
            "sc_count": ["exact", "lt", "gt"],
            "fail_count": ["exact", "lt", "gt"],
            "absent_count": ["exact", "lt", "gt"],
            "highest_score": ["exact", "lt", "gt"],
            "highest_scorer": ["exact"],
        }


class SemesterMetricsFilter(django_filters.FilterSet):
    class Meta:
        model = SemesterMetrics
        fields = {
            "section": ["exact"],
            "semester": ["exact"],
            "avg_sgpa": ["exact", "lt", "gt"],
            "total_backlogs": ["exact", "lt", "gt"],
            "pass_percentage": ["exact", "lt", "gt"],
            "fail_percentage": ["exact", "lt", "gt"],
            "pass_count": ["exact", "lt", "gt"],
            "fail_1_sub": ["exact", "lt", "gt"],
            "fail_2_subs": ["exact", "lt", "gt"],
            "fail_3_subs": ["exact", "lt", "gt"],
            "fail_greater_3_subs": ["exact", "lt", "gt"],
        }
