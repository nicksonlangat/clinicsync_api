# Generated by Django 5.0.4 on 2024-06-05 12:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_user_phone_number"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("Admin", "Admin"),
                    ("Owner", "Owner"),
                    ("Doctor", "Doctor"),
                    ("Staff", "Staff"),
                ],
                default="Admin",
                max_length=20,
            ),
        ),
    ]
