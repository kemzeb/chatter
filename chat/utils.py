import enum


class EventName(enum.StrEnum):
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


class EventErrCode(enum.IntEnum):
    SERIALIZATION = 1
    BAD_MESSAGE = 400
    FORBIDDEN = 403
