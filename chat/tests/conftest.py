import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import ChatGroup
from chatter.asgi import application

User = get_user_model()


@pytest.fixture
def origin_header() -> tuple[bytes, bytes]:
    return (b"origin", b"http://localhost")


@pytest.fixture
def user_1():
    """
    Creates a user and also creates 2 of their own chat groups. They have the following
    names:
    - "Precursors rule"
    - "The Glory Of Panau"
    """
    user1 = User.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )
    group_1 = ChatGroup.objects.create(owner=user1, name="Precursors rule")
    group_2 = ChatGroup.objects.create(owner=user1, name="The Glory Of Panau")
    group_1.members.add(user1)
    group_2.members.add(user1)

    return user1


@pytest.fixture
def communicator1_without_handling(origin_header, user_1) -> WebsocketCommunicator:
    """
    Creates a `WebsocketCommunicator` using the `user_1` fixture. You will need to call
    `connect()` and `disconnect()` on the `WebsocketCommunicator` manually.
    """
    jwt = RefreshToken.for_user(user_1)
    comm = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt.access_token}",
        headers=[origin_header],
    )

    return comm


@pytest_asyncio.fixture
async def communicator1(communicator1_without_handling):
    """
    Provides a `WebsocketCommunicator` that handles triggering connection and
    disconnection. This uses the user_1 fixture, hence the "1" in the fixture name.
    """
    connected, _ = await communicator1_without_handling.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield communicator1_without_handling
    await communicator1_without_handling.disconnect()
