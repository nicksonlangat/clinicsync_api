from django.utils.text import slugify

from core.models import Category, Product, Vendor

from .base_test import BaseTest


class ProductModelTest(BaseTest):
    def test_create_product(self):
        category = Category.objects.create(name="Test Category")
        vendor = vendor = Vendor.objects.create(
            created_by=self.user,
            name="Test Vendor",
            email="test@vendor.com",
            phone_number="123-456-7890",
            location="123 Vendor St",
        )
        product = Product.objects.create(
            created_by=self.user,
            vendor=vendor,
            category=category,
            name="Test Product",
            price=9.99,
        )
        self.assertEqual(str(product), "Test Product")
        self.assertTrue(product.sku.startswith("test-product-".upper()[:3]))

    def test_sku_generation(self):
        product = Product.objects.create(name="Unique Product", price=9.99)
        expected_prefix = slugify("Unique Product")[:3].upper()
        self.assertTrue(product.sku.startswith(f"{expected_prefix}-"))
