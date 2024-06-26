import random
import string

from django.db import models
from django.db.models import F, Sum
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


class Staff(BaseModel):
    class StaffType(models.TextChoices):
        DOCTOR = "Doctor"
        NURSE = "Nurse"
        GENERAL = "General"

    class JobType(models.TextChoices):
        PART = "Part Time"
        FULL = "Full Time"

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_staff", null=True, blank=True
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff")
    job_title = models.CharField(max_length=250, blank=True, null=True)
    staff_type = models.CharField(
        max_length=255, choices=StaffType.choices, default=StaffType.GENERAL
    )
    job_type = models.CharField(
        max_length=255, choices=JobType.choices, default=JobType.FULL
    )
    working_days = models.JSONField()

    def __str__(self) -> str:
        return str(self.job_title)


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
        if not self.sku or self.sku == "":
            self.sku = self.generate_unique_sku()
        super().save(*args, **kwargs)

    def generate_unique_sku(self):
        prefix = slugify(self.name)[:3].upper()
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"{prefix}-{suffix}"

    def __str__(self) -> str:
        return str(self.name)


class Order(BaseModel):
    class Status(models.TextChoices):
        COMPLETE = "Complete"
        PENDING = "Pending"
        CANCELLED = "Cancelled"

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="orders", null=True, blank=True
    )
    vendor = models.ForeignKey(
        Vendor,
        on_delete=models.CASCADE,
        related_name="vendor_orders",
        null=True,
        blank=True,
    )
    order_number = models.CharField(max_length=255, unique=True, blank=True, null=True)
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.PENDING
    )
    notes = models.TextField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.order_number or self.order_number == "":
            self.order_number = self.generate_unique_order_number()
        super().save(*args, **kwargs)

    def generate_unique_order_number(self):
        prefix = "ORD"
        suffix = "".join(random.choices(string.digits, k=5))
        return f"{prefix}-{suffix}"

    def order_totals(self):
        return self.items.all().aggregate(total=Sum("total"))["total"]

    def __str__(self) -> str:
        return str(self.order_number)


class OrderItem(BaseModel):
    class Status(models.TextChoices):
        RECEIVED = "Received"
        PENDING = "Pending"

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="product_items"
    )
    status = models.CharField(
        max_length=255, choices=Status.choices, default=Status.PENDING
    )
    price = models.DecimalField(max_digits=9, decimal_places=2)
    quantity = models.IntegerField(default=1)
    total = models.GeneratedField(
        expression=F("quantity") * F("price"),
        output_field=models.FloatField(),
        db_persist=True,
    )

    def __str__(self) -> str:
        return f"{self.order.order_number} - {self.product.name} - {self.total}"
