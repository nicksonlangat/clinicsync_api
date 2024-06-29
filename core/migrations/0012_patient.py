# Generated by Django 5.0.4 on 2024-06-28 09:10

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0011_staff_created_by"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Patient",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("first_name", models.CharField(blank=True, max_length=250, null=True)),
                ("last_name", models.CharField(blank=True, max_length=250, null=True)),
                (
                    "phone_number",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                ("address", models.CharField(blank=True, max_length=250, null=True)),
                (
                    "gender",
                    models.CharField(
                        choices=[("Male", "Male"), ("Female", "Female")],
                        default="Male",
                        max_length=250,
                    ),
                ),
                (
                    "image",
                    models.ImageField(blank=True, null=True, upload_to="patients"),
                ),
                ("age", models.IntegerField()),
                (
                    "hiv_status",
                    models.CharField(
                        choices=[("Positive", "Positive"), ("Negative", "Negative")],
                        default="Negative",
                        max_length=250,
                    ),
                ),
                (
                    "blood_group",
                    models.CharField(
                        choices=[("A", "A"), ("B", "B"), ("AB", "Ab"), ("O", "O")],
                        default="AB",
                        max_length=250,
                    ),
                ),
                (
                    "blood_pressure",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                ("is_allergic", models.BooleanField(default=False)),
                (
                    "allergic_description",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                ("last_visit", models.DateTimeField(blank=True, null=True)),
                (
                    "clinic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="clinic_patients",
                        to="core.clinic",
                    ),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="patients",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "abstract": False,
            },
        ),
    ]
