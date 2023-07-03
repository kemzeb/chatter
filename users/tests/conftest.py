import pytest
import pytest_asyncio
from channels.testing import WebsocketCommunicator
from rest_framework_simplejwt.tokens import RefreshToken

from chatter.asgi import application
from users.models import ChatterUser


@pytest.fixture
def user_main():
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
async def communicator_main(user_main):
    """
    Provides a `WebsocketCommunicator` that handles triggering connection and
    disconnection. This uses the `user_main` fixture, hence the "1" in the fixture name.

    """
    jwt = RefreshToken.for_user(user_main)
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
def add_multiple_users(user_main):
    """Creates 16 users, 11 being friends of user_main"""
    friends = [
        {"username": "paganmin", "password": "test"},
        {"username": "pacman", "password": "test"},
        {"username": "paynes_me_max", "password": "test"},
        {"username": "Paco", "password": "test"},
        {"username": "spacehunter", "password": "test"},
        {"username": "PackieMcReary", "password": "test"},
        {"username": "pattycakepraxis", "password": "test"},
        {"username": "parker_sector_rocks", "password": "test"},
        {"username": "luikangpang", "password": "test"},
        {"username": "CrateOs", "password": "clonewars"},
        {"username": "you_rePRETTYgood", "password": "mgs"},
    ]
    for f in friends:
        friend = ChatterUser.objects.create(
            username=f["username"], password=f["password"]
        )
        user_main.friends.add(friend)
    ChatterUser.objects.create(username="parabellum", password="test")
    ChatterUser.objects.create(username="pandora", password="test")
    ChatterUser.objects.create(username="eos", password="test")
    ChatterUser.objects.create(username="dust", password="test")
    ChatterUser.objects.create(username="badlands", password="test")
    ChatterUser.objects.create(username="oasis", password="test")


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
