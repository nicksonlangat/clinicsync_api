import datetime
import random
from datetime import timedelta

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from shared.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        first_name = extra_fields.get("first_name", None)
        last_name = extra_fields.get("last_name", None)

        if not email:
            raise ValueError("Email is required.")
        if not first_name:
            raise ValueError("First name is required.")
        if not last_name:
            raise ValueError("Last name is required.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password, **extra_fields):
        first_name = extra_fields.get("first_name", None)
        last_name = extra_fields.get("last_name", None)

        if not email:
            raise ValueError("Email is required.")
        if not first_name:
            raise ValueError("First name is required.")
        if not last_name:
            raise ValueError("Last name is required.")

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must be staff.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must be superuser")

        return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    """Models a single application user."""

    class Role(models.TextChoices):
        ADMIN = "Admin"
        OWNER = "Owner"
        DOCTOR = "Doctor"
        STAFF = "Staff"

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=35, blank=False, null=False, db_index=True)
    last_name = models.CharField(max_length=35, blank=False, null=False, db_index=True)
    phone_number = models.CharField(max_length=250, null=True, blank=True)
    image = models.ImageField(upload_to="profiles", blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    email_confirmed = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ADMIN)

    last_login = None

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    def __str__(self) -> str:
        return str(self.email)

    def to_dict(self, exclude=None, include=None):
        default_exclude = ["password", "is_staff", "is_superuser"]
        if exclude:
            exclude.extend(default_exclude)
        if not exclude:
            exclude = default_exclude
        return super().to_dict(exclude, include)


class PasswordResetToken(BaseModel):
    code = models.IntegerField(null=True, blank=True)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="reset_token"
    )
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self) -> str:
        return str(self.code)

    def save(self, *args, **kwargs):
        self.expires_at = timezone.now() + timedelta(minutes=10)
        self.code = "".join(random.choice("0123456789") for _ in range(6))
        super().save(*args, **kwargs)

    @property
    def has_expired(self) -> bool:
        now = timezone.now()

        return now >= self.expires_at


class Plan(BaseModel):
    class Plans(models.TextChoices):
        TRIAL = "Trial"
        FREE = "Free"
        PRO = "Pro"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_plan"
    )
    expiry_date = models.DateField(null=True, blank=True)
    plan = models.CharField(max_length=10, choices=Plans.choices, default="Trial")

    def __str__(self) -> str:
        return f"{self.plan} - {self.user.email}"

    def save(self, *args, **kwargs):
        # self.expiry_date = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def remaining_days(self) -> bool:
        today = datetime.date.today()

        return (self.expiry_date - today).days
