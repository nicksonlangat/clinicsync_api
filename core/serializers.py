from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Clinic


class ClinicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = "__all__"

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["user"] = UserSerializer(instance.created_by).data
        representation["members"] = UserSerializer(
            instance.members.all(), many=True
        ).data
        return representation
