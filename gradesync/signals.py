# signals.py
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import (
    Score,
    SemesterMetrics,
    Student,
    StudentPerformance,
    Subject,
    SubjectMetrics,
)


@receiver([post_save, post_delete], sender=Subject)
def update_subject_count(sender, instance, **kwargs):
    semester = instance.semester
    semester.count_num_subjects()


@receiver([post_save, post_delete], sender=Student)
def update_student_count(sender, instance, **kwargs):
    section = instance.section
    batch = instance.batch
    section.count_num_students()
    batch.count_num_students()


@receiver([post_save, post_delete], sender=StudentPerformance)
def update_cgpa(sender, instance, **kwargs):
    student = instance.student
    student.calculate_cgpa()
    student.count_num_backlogs()


@receiver([post_save], sender=Score)
def update_student_and_metrics(sender, instance, **kwargs):
    student = instance.student
    semester = instance.semester
    subject = instance.subject

    # Update the student performance metrics
    student_performance = StudentPerformance.objects.get(
        student=student, semester=semester
    )
    student_performance.calculate_all()

    # Update the backlogs for the student
    student.count_num_backlogs()

    # Update the SubjectMetrics
    subject_metrics = SubjectMetrics.objects.get(
        subject=subject, semester=semester, section=student.section
    )
    subject_metrics.calculate_metrics()

    # Update the SemesterMetrics
    semester_metrics = SemesterMetrics.objects.get(
        semester=semester, section=student.section
    )
    semester_metrics.calculate_metrics()
