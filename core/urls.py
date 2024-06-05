# from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"clinics", views.ClinicApi, basename="clinics")


urlpatterns = [
    # path("generate-invoice", views.PDFFromHtmlApi.as_view(), name="invoice-pdf"),
] + router.urls
