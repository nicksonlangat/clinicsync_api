from django.db import models

from accounts.models import User
from shared.models import BaseModel


class Clinic(BaseModel):
    name = models.CharField(max_length=250)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="clinics", null=True, blank=True
    )
    members = models.ManyToManyField(User, blank=True)
    location = models.CharField(max_length=250, null=True, blank=True)
    opening_hour = models.TimeField(null=True, blank=True)
    closing_hour = models.TimeField(null=True, blank=True)
    clinic_email = models.EmailField(null=True, blank=True)
    clinic_phone_number = models.CharField(null=True, blank=True)
    logo = models.ImageField(upload_to="clinic-logos", null=True, blank=True)


class ClinicBranch(BaseModel):
    pass


class Vendor(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="vendors", null=True, blank=True
    )
    name = models.CharField(max_length=250)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    location = models.CharField(max_length=250)
    logo = models.ImageField(upload_to="vendors", null=True, blank=True)

    def __str__(self) -> str:
        return str(self.name)
