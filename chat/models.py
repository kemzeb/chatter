from django.db import models

from chatter import settings


class ChatGroup(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="ChatGroupMembership", related_name="members"
    )
    name = models.CharField(max_length=64)
    date_created = models.DateField(auto_now_add=True)


class ChatGroupMembership(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    data_joined = models.DateField(auto_now_add=True)


class ChatMessage(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    from_chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    message = models.TextField()
    date_sent = models.DateField(auto_now_add=True)


class ChatGroupInvite(models.Model):
    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="from_user"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="to_user"
    )
    chat_group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE)
    date_invited = models.DateField(auto_now_add=True)
