import os
import random

import pandas as pd
from django.conf import settings
from django.db.models import F, Q, Sum
from django.http import FileResponse, HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Category, Clinic, Product, Vendor
from .permissions import IsOwnerPermission
from .serializers import (
    CategorySerializer,
    ClinicSerializer,
    ProductSerializer,
    VendorSerializer,
)


class ClinicApi(viewsets.ModelViewSet):
    queryset = Clinic.objects.all()
    serializer_class = ClinicSerializer
    permission_classes = [IsOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class VendorApi(viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [IsOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return Vendor.objects.filter(created_by=self.request.user)


class CategoryApi(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]


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
                    "stock_number": random.randint(0, 100),
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


class ProductStatsApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        products = Product.objects.filter(created_by=request.user)
        products_count = products.count()
        low_stock_products = products.filter(
            Q(stock_number__lte=20) & Q(stock_number__gt=0)
        ).count()
        out_of_stock_products = products.filter(stock_number=0).count()
        total_product_value = products.aggregate(
            total=Sum(F("price") * F("stock_number"))
        )["total"]
        return Response(
            {
                "total_products": products_count,
                "total_stock_value": total_product_value,
                "low_stock_products": {
                    "value": low_stock_products,
                    "percentage": f"{(low_stock_products / products_count) * 100}%",
                },
                "out_of_stock_products": {
                    "value": out_of_stock_products,
                    "percentage": f"{(out_of_stock_products / products_count) * 100}%",
                },
                "in_stock_products": {
                    "value": products_count
                    - (low_stock_products + out_of_stock_products),
                    "percentage": f"""{(
                        (products_count - (low_stock_products + out_of_stock_products))
                        / products_count
                    )
                    * 100}%""",
                },
            }
        )


class ExportProductsApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        products = Product.objects.all()[:10]
        # Create a DataFrame
        data = {
            "Name": [product.name for product in products],
            "Stock Number": [product.stock_number for product in products],
            "Price": [product.price for product in products],
            "Image URL": [product.image_url for product in products],
        }
        df = pd.DataFrame(data)

        # Create a response object
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = "attachment; filename=products.xlsx"

        # Write the DataFrame to the response object
        df.to_excel(response, index=False, engine="openpyxl")

        return response


class ServeProductsExcelApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        file_path = os.path.join(settings.BASE_DIR, "exports/products.xlsx")
        return FileResponse(
            open(file_path, "rb"), as_attachment=True, filename="products.xlsx"
        )
