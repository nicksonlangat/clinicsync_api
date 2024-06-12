from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"clinics", views.ClinicApi, basename="clinics")
router.register(r"vendors", views.VendorApi, basename="vendors")
router.register(r"products", views.ProductApi, basename="products")
router.register(r"categories", views.CategoryApi, basename="categories")
router.register(r"orders", views.OrderApi, basename="orders")


urlpatterns = [
    path("import/products", views.ImportProductsApi.as_view(), name="import-products"),
    path("import/vendors", views.ImportVendorsApi.as_view(), name="import-vendors"),
    path("products/stats", views.ProductStatsApi.as_view(), name="products-stats"),
    path("export/products", views.ExportProductsApi.as_view(), name="export-products"),
    path(
        "serve/products", views.ServeProductsExcelApi.as_view(), name="serve-products"
    ),
    path(
        "orderitems/<int:pk>/",
        views.OrderItemAPIView.as_view(),
        name="order-item-detail",
    ),
] + router.urls
