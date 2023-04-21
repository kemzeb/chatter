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
