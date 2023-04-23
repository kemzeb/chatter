from enum import Enum


class EventName(Enum):
    GROUP_CONNECT = "group:connect"
    GROUP_CREATE = "group:create"
    GROUP_FETCH = "group:fetch"
    GROUP_MESSAGE = "group:message"
    USER_FRIEND_REQUEST = "user:friendrequest"


class EventErrCode(Enum):
    SERIALIZATION = 1
    BAD_MESSAGE = 400
    FORBIDDEN = 403
