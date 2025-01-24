# signals.py
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Student, Subject


@receiver([post_save, post_delete], sender=Subject)
def update_subject_count(sender, instance, **kwargs):
    semester = instance.sem
    semester.count_num_subjects()


@receiver([post_save, post_delete], sender=Student)
def update_student_count(sender, instance, **kwargs):
    section = instance.section
    batch = instance.batch
    section.count_num_students()
    batch.count_num_students()
