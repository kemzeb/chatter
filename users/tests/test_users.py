import json

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import force_authenticate

from users.views import FriendsListView


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
def test_friends_list_view(user_1):
    factory = RequestFactory()
    view = FriendsListView.as_view()

    request = factory.get(f"/api/users/{user_1.id}/friends/")
    force_authenticate(request, user=user_1)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 2
