import random
import string

from django.db import models
from django.utils.text import slugify

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


class Category(BaseModel):
    name = models.CharField(max_length=250)

    def __str__(self) -> str:
        return str(self.name)


class Product(BaseModel):
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="products", null=True, blank=True
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="vendor_products",
        null=True,
        blank=True,
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="category_products",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    sku = models.CharField(max_length=255, unique=True, blank=True, null=True)
    stock_number = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    image_url = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to="products", null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = self.generate_unique_sku()
        super().save(*args, **kwargs)

    def generate_unique_sku(self):
        prefix = slugify(self.name)[:3].upper()
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"{prefix}-{suffix}"

    def __str__(self) -> str:
        return str(self.name)
