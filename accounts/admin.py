from django.contrib import admin

from .models import Plan, User

# Register your models here.

admin.site.register(User)
admin.site.register(Plan)
