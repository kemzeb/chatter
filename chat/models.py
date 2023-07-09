from django.db import models
from django.utils.timezone import now

from chatter import settings


class ChatGroup(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="ChatGroupMembership",
        related_name="chat_groups",
    )
    name = models.CharField(max_length=64)
    created = models.DateTimeField(default=now)


class ChatGroupMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    joined = models.DateTimeField(default=now)


class ChatMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(
        ChatGroup, on_delete=models.CASCADE, related_name="messages"
    )
    message = models.CharField(max_length=1800)
    created = models.DateTimeField(default=now)
