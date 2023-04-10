from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ChatterUser

admin.site.register(ChatterUser, UserAdmin)
