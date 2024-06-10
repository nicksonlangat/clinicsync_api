from core.models import Vendor

from .base_test import BaseTest


class VendorModelTest(BaseTest):
    def test_create_vendor(self):
        vendor = Vendor.objects.create(
            created_by=self.user,
            name="Test Vendor",
            email="test@vendor.com",
            phone_number="123-456-7890",
            location="123 Vendor St",
        )
        self.assertEqual(str(vendor), "Test Vendor")
