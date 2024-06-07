import pandas as pd
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Clinic, Vendor
from .permissions import IsOwnerPermission
from .serializers import ClinicSerializer, VendorSerializer


class ClinicApi(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    # def get_queryset(self):
    #     return Client.objects.filter(user=self.request.user)


class VendorApi(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ImportVendorsApi(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, format=None):
        file_obj = request.data["file"]
        try:
            # Read the Excel file
            df = pd.read_excel(file_obj)

            # Validate and save each row
            vendors = []
            for _, row in df.iterrows():
                vendor_data = {
                    "name": row.get("name"),
                    "created_by": request.user.id,
                    "location": row.get("location"),
                    "phone_number": row.get("phone_number"),
                    "email": row.get("email"),
                }
                serializer = VendorSerializer(data=vendor_data)
                if serializer.is_valid():
                    vendors.append(serializer.save())
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {
                    "status": "success",
                    "clients": VendorSerializer(vendors, many=True).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
