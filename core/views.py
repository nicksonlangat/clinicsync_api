import calendar
import datetime
import logging
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

from shared.pdf import Pdf

from .models import (
    Category,
    Clinic,
    Order,
    OrderItem,
    Patient,
    Product,
    Reservation,
    Staff,
    Vendor,
)
from .permissions import IsOwnerPermission
from .serializers import (
    CategorySerializer,
    ClinicSerializer,
    OrderItemSerializer,
    OrderSerializer,
    PatientSerializer,
    ProductSerializer,
    ReservationSerializer,
    StaffSerializer,
    VendorSerializer,
)
from .utils import send_order_email_to_vendor

logger = logging.getLogger(__name__)


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


class OrderApi(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsOwnerPermission]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = Order.objects.filter(created_by=self.request.user)
        status = self.request.query_params.get("status", None)
        order_number = self.request.query_params.get("order_number", None)
        vendor = self.request.query_params.get("vendor", None)

        if order_number:
            qs = qs.filter(order_number=order_number)
        if vendor:
            qs = qs.filter(vendor=vendor)
        if status:
            qs = qs.filter(status=status)
        return qs


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
        qs = Product.objects.filter(created_by=self.request.user)[:20]
        status = self.request.query_params.get("status", None)
        stock_number = self.request.query_params.get("stock_number", None)
        category = self.request.query_params.get("category", None)
        vendor = self.request.query_params.get("vendor", None)
        sku = self.request.query_params.get("sku", None)
        name = self.request.query_params.get("name", None)

        if sku:
            qs = qs.filter(sku=sku)
        if stock_number:
            qs = qs.filter(stock_number=stock_number)
        if category:
            qs = qs.filter(category=category)
        if vendor:
            qs = qs.filter(vendor=vendor)
        if status:
            if status == "low_stock":
                qs = qs.filter(Q(stock_number__lte=20) & Q(stock_number__gt=0))
            if status == "out_of_stock":
                qs = qs.filter(stock_number=0)
            if status == "in_stock":
                qs = qs.filter(stock_number__gt=20)
        if name:
            qs = (
                qs.filter(name__contains=name.upper()).order_by("name").distinct("name")
            )
        return qs


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
                "total_stock_value": total_product_value if total_product_value else 0,
                "low_stock_products": {
                    "value": low_stock_products,
                    "percentage": f"{(low_stock_products / products_count) * 100}%"
                    if products_count
                    else 0,
                },
                "out_of_stock_products": {
                    "value": out_of_stock_products,
                    "percentage": f"{(out_of_stock_products / products_count) * 100}%"
                    if products_count
                    else 0,
                },
                "in_stock_products": {
                    "value": products_count
                    - (low_stock_products + out_of_stock_products),
                    "percentage": f"""{(
                        (products_count - (low_stock_products + out_of_stock_products))
                        / products_count
                    )
                    * 100}%"""
                    if products_count
                    else 0,
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


class OrderItemApi(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [IsOwnerPermission]


class TestEmailApi(APIView):
    def get(self, request, format=None):
        order = Order.objects.first()
        email_sent = send_order_email_to_vendor(order, request)

        return Response({"sent": email_sent})


class TestPdfApi(APIView):
    def get(self, request, format=None):
        order = Order.objects.first()
        items = order.items.all()
        clinic = order.created_by.clinics.all()[0]

        selected_template = "order"
        return (
            Pdf()
            .generate_pdf(
                request,
                selected_template,
                {"order": order, "items": items, "clinic": clinic},
            )
            .to_response(disposition="inline")
        )


class ChangeOrderStatusApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        order_id = request.data.get("order_id")
        new_status = request.data.get("status")
        order = Order.objects.get(id=order_id)

        if new_status and new_status in [
            Order.Status.COMPLETE,
            Order.Status.PENDING,
            Order.Status.CANCELLED,
        ]:
            order.status = new_status
            order.save()
            return Response({"status": "status updated"}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)


class SendOrderEmailApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        order_id = request.data.get("order_id")
        order = Order.objects.get(id=order_id)

        email_sent = send_order_email_to_vendor(order, request)
        if email_sent:
            logger.info(f"The email has been sent for {order.order_number}")
            order.email_sent = True
            order.save()
            return Response({"status": "email sent"}, status=status.HTTP_200_OK)
        return Response(
            {"error": "Error sending email"}, status=status.HTTP_400_BAD_REQUEST
        )


class StaffApi(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsOwnerPermission]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        qs = Staff.objects.filter(created_by=self.request.user)
        staff_type = self.request.query_params.get("staff_type", None)
        job_type = self.request.query_params.get("job_type", None)
        job_type = self.request.query_params.get("job_type", None)
        job_title = self.request.query_params.get("job_title", None)
        if staff_type is not None and staff_type != "":
            qs = qs.filter(staff_type=staff_type)
        if job_type is not None and job_type != "":
            qs = qs.filter(Q(job_type=job_type))
        if job_title is not None and job_title != "":
            qs = qs.filter(job_title=job_title)

        return qs


class ClinicStaffStatsApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        qs = Staff.objects.filter(created_by=self.request.user)
        doctor_count = qs.filter(staff_type="Doctor").count()
        nurse_count = qs.filter(staff_type="Nurse").count()
        general_count = qs.filter(staff_type="General").count()

        return Response(
            {
                "doctor_count": doctor_count,
                "nurse_count": nurse_count,
                "general_count": general_count,
            },
            status=status.HTTP_200_OK,
        )


class PatientApi(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        clinic = Clinic.objects.filter(created_by=self.request.user).first()
        qs = Patient.objects.filter(clinic=clinic)
        hiv_status = self.request.query_params.get("hiv_status", None)
        blood_group = self.request.query_params.get("blood_group", None)
        is_active = self.request.query_params.get("is_active")
        gender = self.request.query_params.get("gender", None)

        if is_active is not None and is_active != "":
            is_active = is_active.lower() == "true"
            qs = qs.filter(is_active=is_active)
        if hiv_status is not None and hiv_status != "":
            qs = qs.filter(Q(hiv_status=hiv_status))
        if blood_group is not None and blood_group != "":
            qs = qs.filter(blood_group=blood_group)
        if gender is not None and gender != "":
            qs = qs.filter(gender=gender)

        return qs


class ClinicPatientStatsApi(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        clinic = Clinic.objects.filter(created_by=self.request.user).first()
        qs = Patient.objects.filter(clinic=clinic)

        return Response(
            {
                "active_patient_count": qs.filter(is_active=True).count(),
                "inactive_patient_count": qs.filter(is_active=False).count(),
                "total_count": qs.count(),
            },
            status=status.HTTP_200_OK,
        )


class ReservationApi(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class WeeklyAppointmentApi(APIView):
    permission_classes = [permissions.AllowAny]

    def get_current_week_dates(self):
        today = datetime.date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        current_week_dates = [
            start_of_week + datetime.timedelta(days=i) for i in range(5)
        ]
        return current_week_dates

    def get(self, request):
        dates = self.get_current_week_dates()
        # Filter reservations for each date
        reservations_by_date = []
        for date in dates:
            reservations = Reservation.objects.filter(reservation_date=date).order_by(
                "start_time"
            )
            serializer = ReservationSerializer(reservations, many=True)
            reservations_by_date.append(
                {
                    "date": date.day,  # date.strftime("%Y-%m-%d"),
                    "day": calendar.day_name[date.weekday()][:3],
                    "today": datetime.date.today().day == date.day,
                    "appointments": serializer.data,
                }
            )

        return Response({"results": reservations_by_date})
