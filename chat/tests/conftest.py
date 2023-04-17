import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from chatter.asgi import application

User = get_user_model()


@pytest.fixture
def origin_header() -> tuple[bytes, bytes]:
    return (b"origin", b"http://localhost")


@pytest.fixture
def user_1():
    user1 = User.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )
    return user1


@pytest.fixture
def communicator_user_1_no_connect_trigger(
    origin_header, user_1
) -> WebsocketCommunicator:
    """
    A fixture that exists to test ChatConsumer connections. You will need to call
    connect() and disconnect() on the WebsocketCommunicator manually.
    """
    jwt = RefreshToken.for_user(user_1)
    comm = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt.access_token}",
        headers=[origin_header],
    )

    return comm


@pytest_asyncio.fixture
async def communicator_user_1(communicator_user_1_no_connect_trigger, user_1):
    """
    A fixture that provides a WebsocketCommunicator that handles triggering connection
    and disconnection.
    """
    connected, _ = await communicator_user_1_no_connect_trigger.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield communicator_user_1_no_connect_trigger
    await communicator_user_1_no_connect_trigger.disconnect()
