from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from gradesync.models import User


class Command(BaseCommand):
    """
    Create default groups and permissions.
    HODs: add_user, change_user, delete_user permissions (only for Teachers and Students)
    Teachers: add_user, change_user, delete_user permissions (only for Students)
    Students: No permissions
    """

    help = "Create default groups and permissions"

    def handle(self, *args, **kwargs):
        # Define your groups and permissions here
        groups_permissions = {
            "HODs": ["add_user", "change_user", "delete_user"],
            "Teachers": ["add_user", "change_user", "delete_user"],
            "Students": [],  # No permissions for students
        }

        # Get the User model's content type
        user_content_type = ContentType.objects.get_for_model(User)

        for group_name, permissions in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group {group_name}"))
            for perm in permissions:
                permission, perm_created = Permission.objects.get_or_create(
                    codename=perm,
                    name=f'Can {perm.replace("_", " ")}',
                    content_type=user_content_type,
                )
                group.permissions.add(permission)
            group.save()
            self.stdout.write(
                self.style.SUCCESS(f"Updated group {group_name} with permissions")
            )
