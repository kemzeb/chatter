from django.contrib.auth.models import AbstractUser
from django.db import models

from chatter.settings import AUTH_USER_MODEL


class ChatterUser(AbstractUser):
    friends = models.ManyToManyField("self", through="Friendship")


class Friendship(models.Model):
    from_user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    to_user = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+"
    )
    date_started = models.DateField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["from_user", "to_user"],
                name="a_one_way_friendship_is_unique",
            ),
        ]


class FriendRequest(models.Model):
    requester = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests"
    )
    addressee = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pending_requests"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["requester", "addressee"],
                name="requester_addressee_unique",
            ),
        ]
