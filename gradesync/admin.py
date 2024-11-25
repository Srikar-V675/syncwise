from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .forms import UserAdminForm
from .models import (
    Batch,
    BatchAdmin,
    Department,
    Section,
    SectionAdmin,
    Semester,
    SemesterAdmin,
    Student,
    StudentAdmin,
    User,
)


class CustomUserAdmin(BaseUserAdmin):
    form = UserAdminForm

    # Fieldsets for updating existing users
    # TODO: Order the fields in the fieldsets
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "department")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fieldsets for creating new users
    # TODO: Order the fields in the fieldsets
    add_fieldsets = (
        (None, {"fields": ("username", "password1", "password2")}),
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "department")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            # If no object, it means we are adding a new user
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.groups.filter(name="HODs").exists():
            # Filter by group name (Teachers or Students) and department
            return qs.filter(
                groups__name__in=["Teachers", "Students"],
                department=request.user.department,
            )
        elif request.user.groups.filter(name="Teachers").exists():
            # Filter by department and group name (Students)
            return qs.filter(
                department=request.user.department, groups__name="Students"
            )
        return qs

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # Creating a new user
            obj.department = request.user.department
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "groups" in form.base_fields:
            if request.user.groups.filter(name="HODs").exists():
                # Set the groups field to Teachers and Students.
                form.base_fields["groups"].queryset = Group.objects.filter(
                    name__in=["Teachers", "Students"]
                )
                # Set the department field to the current user's department and disable it
                form.base_fields["department"].initial = request.user.department
                form.base_fields["department"].disabled = True
            elif request.user.groups.filter(name="Teachers").exists():
                # Set the groups field to Students
                form.base_fields["groups"].queryset = Group.objects.filter(
                    name="Students"
                )
                # Set the department field to the current user's department and disable it
                form.base_fields["department"].initial = request.user.department
                form.base_fields["department"].disabled = True
        return form


admin.site.register(User, CustomUserAdmin)
admin.site.register(Department)
admin.site.register(Batch, BatchAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Student, StudentAdmin)
