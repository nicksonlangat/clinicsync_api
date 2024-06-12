from django.contrib import admin

from .models import Category, Order, OrderItem, Product, Vendor

# Register your models here.

admin.site.register(Product)
admin.site.register(Vendor)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)
