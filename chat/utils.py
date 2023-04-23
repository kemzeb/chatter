import enum


class EventName(enum.StrEnum):
    GROUP_CONNECT = "group:connect"
    GROUP_CREATE = "group:create"
    GROUP_FETCH = "group:fetch"
    GROUP_MESSAGE = "group:message"
    GROUP_ADD = "group:add"
    USER_FRIEND_REQUEST = "user:friendrequest"
    ERROR_EVENT = "error"

    def __str__(self) -> str:
        return self.value


class EventErrCode(enum.IntEnum):
    SERIALIZATION = 1
    BAD_MESSAGE = 400
    FORBIDDEN = 403
