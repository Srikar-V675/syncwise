from django.contrib.auth.models import Group
from rest_framework import serializers

from .models import Student, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name")

    def create(self, validated_data):
        # assign group to user
        user = super().create(validated_data)
        group = Group.objects.get(name="Students")
        user.groups.add(group)

        teacher = self.context["request"].user
        user.department = teacher.department

        user.set_password(validated_data["password"])
        user.save()
        return user


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = "__all__"
