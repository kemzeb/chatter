import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from chatter.asgi import application
from users.models import ChatterUser


@pytest.fixture
def user_1():
    """
    Creates 4 users, and returns a user that is friends with 2 of them.
    """
    user1 = ChatterUser.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )
    user1.friends.create(
        username="praxis",
        email="praxis@havencity.org",
        password="giveUpyour13FreeDOM",
    )
    user1.friends.create(
        username="voxx",
        email="voxx@dreadzone.com",
        password="kajsdfjal23542Aw",
    )

    ChatterUser.objects.create(
        username="sewer_crystals_lover",
        email="theplumber@solanaplumbing.com",
        password="rac1rac2rac3",
    )

    return user1


@pytest_asyncio.fixture
async def communicator_1(user_1):
    """
    Provides a `WebsocketCommunicator` that handles triggering connection and
    disconnection. This uses the `user_1` fixture, hence the "1" in the fixture name.

    """
    jwt = RefreshToken.for_user(user_1)
    comm = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt.access_token}",
        headers=[(b"origin", b"http://localhost")],
    )
    connected, _ = await comm.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield comm
    await comm.disconnect()


@pytest.fixture
def add_multiple_users():
    ChatterUser.objects.create(username="luikangpang", password="clonewars")
    ChatterUser.objects.create(username="paganmin", password="test")
    ChatterUser.objects.create(username="pattycakepraxis", password="test")
    ChatterUser.objects.create(username="pacman", password="test")
    ChatterUser.objects.create(username="paynes_me_max", password="test")
    ChatterUser.objects.create(username="parabellum", password="test")
    ChatterUser.objects.create(username="Paco", password="test")
    ChatterUser.objects.create(username="spacehunter", password="test")
    ChatterUser.objects.create(username="PackieMcReary", password="test")
    ChatterUser.objects.create(username="pandora", password="test")
    ChatterUser.objects.create(username="eos", password="test")
    ChatterUser.objects.create(username="parker", password="test")
    ChatterUser.objects.create(username="dust", password="test")
    ChatterUser.objects.create(username="badlands", password="test")
    ChatterUser.objects.create(username="oasis", password="test")
    ChatterUser.objects.create(username="CrateOs", password="test")
    ChatterUser.objects.create(username="you_rePRETTYgood", password="mgs")


@pytest.fixture
def user_drek():
    """
    A user whose friends with no one.
    """
    user = ChatterUser.objects.create(
        username="drekthechairman",
        email="drek@orxon.com",
        password="tryNottoLeaveanyMarks>:)",
    )

    return user


@pytest_asyncio.fixture
async def communicator_drek(user_drek):
    """
    A `WebsocketCommunicator` associated to `user_drek`.
    """
    jwt = RefreshToken.for_user(user_drek)
    comm = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt.access_token}",
        headers=[(b"origin", b"http://localhost")],
    )
    connected, _ = await comm.connect()
    if not connected:
        pytest.fail("WebsocketCommunicator failed to connect.")

    yield comm
    await comm.disconnect()
