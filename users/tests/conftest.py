import pytest

from users.models import ChatterUser


@pytest.fixture
def user_1():
    """
    Creates a 3 users, and returns a user that is friends with 2 of them.
    """
    user1 = ChatterUser.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )
    user1.friends.create(
        username="drek_the_chairman",
        email="drek@oxron.com",
        password="you!&couldntTPossiBLYUNDER127Standxa",
    )
    user1.friends.create(
        username="voxx",
        email="voxx@dreadzone.com",
        password="kajsdfjal23542Aw",
    )

    return user1


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
