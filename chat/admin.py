from django.contrib import admin

from .models import ChatGroup, ChatGroupMembership, ChatMessage

admin.site.register(ChatGroup)
admin.site.register(ChatMessage)
admin.site.register(ChatGroupMembership)
