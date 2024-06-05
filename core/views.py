from rest_framework import viewsets

from .models import Clinic
from .permissions import IsOwnerPermission
from .serializers import ClinicSerializer


class ClinicApi(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsOwnerPermission]
