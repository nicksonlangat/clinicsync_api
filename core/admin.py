from django.contrib import admin

from .models import Category, Product, Vendor

# Register your models here.

admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Category)
