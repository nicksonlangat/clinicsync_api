from core.models import Category

from .base_test import BaseTest


class CategoryModelTest(BaseTest):
    def test_create_category(self):
        category = Category.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")
