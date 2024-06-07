import random

import pandas as pd
from rest_framework import status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Clinic, Product, Vendor
from .permissions import IsOwnerPermission
from .serializers import ClinicSerializer, ProductSerializer, VendorSerializer


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

    def get_queryset(self):
        return Vendor.objects.filter(created_by=self.request.user)


class ProductApi(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return Product.objects.filter(created_by=self.request.user)


class ImportVendorsApi(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsOwnerPermission]

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
                    "phone_number": row.get("contact_number"),
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


class ImportProductsApi(APIView):
    parser_classes = [MultiPartParser]
    permission_classes = [IsOwnerPermission]

    def post(self, request, format=None):
        file_obj = request.data["file"]
        try:
            # Read the Excel file
            df = pd.read_excel(file_obj)

            # Validate and save each row
            products = []
            categories = Category.objects.all()
            vendors = Vendor.objects.filter(created_by=request.user)
            for _, row in df.iterrows():
                product_data = {
                    "name": row.get("name"),
                    "created_by": request.user.id,
                    "image_url": row.get("image"),
                    "price": row.get("price").replace(",", ""),
                    "stock_number": random.randint(5, 800),
                    "vendor": random.choice(vendors).id,
                    "category": random.choice(categories).id,
                }
                serializer = ProductSerializer(data=product_data)
                if serializer.is_valid():
                    products.append(serializer.save())
                else:
                    return Response(
                        serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {
                    "status": "success",
                    "clients": ProductSerializer(products, many=True).data,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
