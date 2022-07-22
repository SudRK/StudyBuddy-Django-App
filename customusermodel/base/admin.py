from django.contrib import admin
import django.db

# Register your models here.

from .models import User

admin.site.register(User)