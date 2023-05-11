import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from chat.models import ChatGroup, ChatMessage
from chatter.asgi import application
from users.models import ChatterUser

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

    It also adds 2 messages to the first chat group that the user made.
    """
    user1 = User.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )
    group_1 = ChatGroup.objects.create(owner=user1, name="Precursors rule")
    group_2 = ChatGroup.objects.create(owner=user1, name="The Glory Of Panau")
    group_1.members.add(user1)
    group_2.members.add(user1)

    ChatMessage.objects.create(user=user1, chat_group=group_1, message="Qwarktastic!")
    ChatMessage.objects.create(
        user=user1,
        chat_group=group_1,
        message="That poor plumber and his social economic disparity.",
    )

    return user1


@pytest.fixture
def user_2():
    """
    A user whose not apart of any chat groups nor has any friends.
    """
    user2 = ChatterUser.objects.create(
        username="markoftheoutsider",
        email="mark@example.com",
        password="bestiesxBWAWithCorvo!!",
    )

    return user2


@pytest.fixture
def user_drek(user_1):
    """
    A user whose friends with `user_1` and is in their "Precursors rule" chat group.
    """
    user3 = ChatterUser.objects.create(
        username="drekthechairman",
        email="drek@orxon.com",
        password="tryNottoLeaveanyMarks>:)",
    )
    user3.friends.add(user_1)

    chat_group = ChatGroup.objects.get(name="Precursors rule")
    chat_group.members.add(user3)

    return user3


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
    disconnection. This uses the `user_1` fixture, hence the "1" in the fixture name.
    """
    connected, _ = await communicator1_without_handling.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield communicator1_without_handling
    await communicator1_without_handling.disconnect()


@pytest_asyncio.fixture
async def communicator2(user_2, origin_header):
    """
    Just like `communicator1` but uses a channel associated to `user_2`.
    """
    jwt = RefreshToken.for_user(user_2)
    comm = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt.access_token}",
        headers=[origin_header],
    )
    connected, _ = await comm.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield comm
    await comm.disconnect()


@pytest_asyncio.fixture
async def communicator_drek(user_drek, origin_header):
    """
    Just like `communicator1` but uses a channel associated to `user_drek`.
    """
    jwt = RefreshToken.for_user(user_drek)
    comm = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt.access_token}",
        headers=[origin_header],
    )
    connected, _ = await comm.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield comm
    await comm.disconnect()
