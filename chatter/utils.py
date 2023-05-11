import enum


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
