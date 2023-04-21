from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ChatterUser, Friendship

admin.site.register(ChatterUser, UserAdmin)
admin.site.register(Friendship)
