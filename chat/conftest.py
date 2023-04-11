import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def jwt_access_token_of_auth_user() -> str:
    user = User.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )

    refresh = RefreshToken.for_user(user)

    return str(refresh.access_token)


@pytest.fixture
def origin_header() -> tuple[bytes, bytes]:
    return (b"origin", b"http://localhost")
