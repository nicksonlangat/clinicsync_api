from core.models import Clinic

from .base_test import BaseTest


class ClinicModelTest(BaseTest):
    def test_create_clinic(self):
        clinic = Clinic.objects.create(
            name="Test Clinic",
            created_by=self.user,
            location="123 Test St",
            clinic_email="test@clinic.com",
            clinic_phone_number="123-456-7890",
        )
        self.assertEqual(clinic.name, "Test Clinic")
        self.assertEqual(clinic.created_by, self.user)
