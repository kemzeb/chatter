import pytest
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture
def user_created_return_jwt_access_token() -> str:
    user = User.objects.create(
        username="qwarkinator", email="qwark@example.com", password="fight_crime!12"
    )

    refresh = RefreshToken.for_user(user)

    return str(refresh.access_token)
