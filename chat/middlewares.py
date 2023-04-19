"""
Reference: https://github.com/joshua-hashimoto/django-channels-jwt-auth-middleware/blob/main/django_channels_jwt_auth_middleware/auth.py # noqa: E501
"""
import traceback
from urllib.parse import parse_qs

from channels.auth import AuthMiddlewareStack
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.db import close_old_connections
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from jwt import decode as jwt_decode

User = get_user_model()


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            if jwt_token_list := parse_qs(scope["query_string"].decode("utf8")).get(
                "token", None
            ):
                jwt_token = jwt_token_list[0]
                jwt_payload = self.get_payload(jwt_token)
                user_credentials = self.get_user_credentials(jwt_payload)
                user = await self.get_logged_in_user(user_credentials)
                scope["user"] = user
            else:
                scope["user"] = AnonymousUser()
        except (InvalidSignatureError, KeyError, ExpiredSignatureError, DecodeError):
            traceback.print_exc()
        except Exception:
            scope["user"] = AnonymousUser()
        return await self.app(scope, receive, send)

    def get_payload(self, jwt_token):
        payload = jwt_decode(jwt_token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload

    def get_user_credentials(self, payload):
        """
        Retrieve user credentials from jwt token payload.
        Defaults to user id.
        """
        user_id = payload["user_id"]
        return user_id

    async def get_logged_in_user(self, user_id):
        user = await get_user(user_id)
        return user


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
