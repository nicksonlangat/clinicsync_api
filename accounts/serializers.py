from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import Plan


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "image",
            "is_superuser",
            "created_at",
            "is_active",
            "email_confirmed",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["full_name"] = f"{instance.first_name} {instance.last_name}"
        return representation


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = fields = ["email", "password", "first_name", "last_name"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = get_user_model()(**validated_data)
        user.set_password(validated_data["password"])
        user.is_active = True
        user.email_confirmed = False
        user.save()
        plan, _ = Plan.objects.get_or_create(user=user)

        return user


class PlanSerializer(serializers.ModelSerializer):
    remaining_days = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = "__all__"
        model = Plan

    def get_remaining_days(self, obj):
        return obj.remaining_days
