from rest_framework.pagination import LimitOffsetPagination


class FriendSearchPagination(LimitOffsetPagination):
    default_limit = 8
    max_limit = 12
