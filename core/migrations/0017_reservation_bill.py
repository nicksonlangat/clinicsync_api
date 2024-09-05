# Generated by Django 5.0.4 on 2024-07-03 04:29

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0016_patient_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="Reservation",
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
                (
                    "reservation_number",
                    models.CharField(blank=True, null=True, unique=True),
                ),
                ("reservation_date", models.DateField(blank=True, null=True)),
                ("start_time", models.TimeField(blank=True, null=True)),
                ("end_time", models.TimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Complete", "Complete"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="Pending",
                        max_length=255,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                ("treatment", models.TextField(blank=True, null=True)),
                (
                    "doctor",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="doctor_reservations",
                        to="core.staff",
                    ),
                ),
                (
                    "patient",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="patient_reservations",
                        to="core.patient",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Bill",
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
                ("bill_number", models.CharField(blank=True, null=True, unique=True)),
                ("paid_at", models.DateTimeField(blank=True, null=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Complete", "Complete"),
                            ("Cancelled", "Cancelled"),
                        ],
                        default="Pending",
                        max_length=255,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "reservation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="bills",
                        to="core.reservation",
                    ),
                ),
            ],
            options={
                "ordering": ["-updated_at"],
                "abstract": False,
            },
        ),
    ]
