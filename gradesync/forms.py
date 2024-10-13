from django import forms
from django.contrib.auth.models import Group

from .models import User


class UserAdminForm(forms.ModelForm):
    class Meta:
        model = User
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.get("instance")
        if user:
            if user.groups.filter(name="HODs").exists():
                self.fields["groups"].queryset = Group.objects.filter(
                    name__in=["Teachers", "Students"]
                )
            elif user.groups.filter(name="Teachers").exists():
                self.fields["groups"].queryset = Group.objects.filter(name="Students")
