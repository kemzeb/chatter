from django.contrib import admin

from .models import ChatGroup, ChatMessage

admin.site.register(ChatGroup)
admin.site.register(ChatMessage)
