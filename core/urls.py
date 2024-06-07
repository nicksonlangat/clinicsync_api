from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"clinics", views.ClinicApi, basename="clinics")
router.register(r"vendors", views.VendorApi, basename="vendors")
router.register(r"products", views.ProductApi, basename="products")


urlpatterns = [
    path("import/products", views.ImportProductsApi.as_view(), name="import-products"),
    path("import/vendors", views.ImportVendorsApi.as_view(), name="import-vendors"),
] + router.urls
