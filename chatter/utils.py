import enum
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chat.models import ChatGroup
from users.models import ChatterUser


def publish_to_user(user: ChatterUser, data: Any, handler: str) -> None:
    """Publishes a WebSocket event to a user associated to a `WebSocketConsumer`
    instance."""
    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            get_channel_group_name(user.username),
            {"type": handler, **data},
        )


def publish_to_group(chat_group: ChatGroup | Any, data: Any, handler: str) -> None:
    """
    Publishes a WebSocket event to a Django Channels group.

    For `chat_group`, pass either a `ChatGroup` or a value that is used throughout the
    project to uniquely identify a chat group's named Channels group.
    """
    unique_id = chat_group

    if type(chat_group) == ChatGroup:
        unique_id = chat_group.pk

    channel_layer = get_channel_layer()
    if channel_layer is not None:
        async_to_sync(channel_layer.group_send)(
            get_group_name(unique_id),
            {"type": handler, **data},
        )


def get_group_name(unqiue_id) -> str:
    """
    Returns a group name. `unique_id` is a value that will be converted to `str`, one
    that uniquely represents the group.
    """
    return f"chat_{str(unqiue_id)}"


def get_channel_group_name(unqiue_id) -> str:
    """
    Returns the group name that is used to uniquely identify a channel. `unique_id` is
    a value that will be converted to `str`, one that uniquely represents the channel.
    """
    return f"user_{str(unqiue_id)}"


class EventName(enum.StrEnum):
    """Represents WebSocket events."""

    GROUP_CONNECT = "group:connect"
    GROUP_CREATE = "group:create"
    GROUP_DESTROY = "group:destroy"
    GROUP_FETCH = "group:fetch"
    GROUP_MESSAGE = "group:message"
    GROUP_ADD = "group:add"
    GROUP_REMOVE = "group:remove"
    USER_FRIEND_REQUEST = "user:friendrequest"
    USER_ACCEPT_FRIEND_REQUEST = "user:accept"
    ERROR_EVENT = "error"

    def __str__(self) -> str:
        return self.value
