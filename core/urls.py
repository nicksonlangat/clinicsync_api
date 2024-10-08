from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"clinics", views.ClinicApi, basename="clinics")
router.register(r"vendors", views.VendorApi, basename="vendors")
router.register(r"products", views.ProductApi, basename="products")
router.register(r"categories", views.CategoryApi, basename="categories")
router.register(r"orders", views.OrderApi, basename="orders")
router.register(r"orderitems", views.OrderItemApi, basename="orderitems")
router.register(r"staff", views.StaffApi, basename="staff")
router.register(r"patients", views.PatientApi, basename="patients")
router.register(r"reservations", views.ReservationApi, basename="reservations")

urlpatterns = [
    path("import/products", views.ImportProductsApi.as_view(), name="import-products"),
    path("import/vendors", views.ImportVendorsApi.as_view(), name="import-vendors"),
    path("products/stats", views.ProductStatsApi.as_view(), name="products-stats"),
    path("export/products", views.ExportProductsApi.as_view(), name="export-products"),
    path(
        "serve/products", views.ServeProductsExcelApi.as_view(), name="serve-products"
    ),
    path("change/status", views.ChangeOrderStatusApi.as_view(), name="change-status"),
    path("send/email", views.SendOrderEmailApi.as_view(), name="send-email"),
    path("test/email", views.TestEmailApi.as_view(), name="email-test"),
    path("test/pdf", views.TestPdfApi.as_view(), name="email-pdf"),
    path("staff/stats", views.ClinicStaffStatsApi.as_view(), name="staff-stats"),
    path("patient/stats", views.ClinicPatientStatsApi.as_view(), name="patient-stats"),
    path(
        "weekly/appointments",
        views.WeeklyAppointmentApi.as_view(),
        name="weekly-appointments",
    ),
] + router.urls
