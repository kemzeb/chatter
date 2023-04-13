import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from chatter.asgi import application

User = get_user_model()


@pytest.fixture
def user_1():
    user1 = User.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )
    user1.save()

    return user1


@pytest.fixture
def jwt_of_user_1(user_1):
    jwt = RefreshToken.for_user(user_1)
    return jwt


@pytest.fixture
def communicator_user_1(jwt_of_user_1, origin_header) -> WebsocketCommunicator:
    return WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt_of_user_1.access_token}",
        headers=[origin_header],
    )


@pytest.fixture
def origin_header() -> tuple[bytes, bytes]:
    return (b"origin", b"http://localhost")
