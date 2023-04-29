import json

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import force_authenticate

from users.views import FriendsListView, UserSearchView


@pytest.mark.django_db
def test_friends_list_view(user_1):
    factory = RequestFactory()
    view = FriendsListView.as_view()

    request = factory.get("/api/users/friends/")
    force_authenticate(request, user=user_1)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 2


@pytest.mark.django_db
@pytest.mark.usefixtures("add_multiple_users")
def test_user_search_view(user_1):
    factory = RequestFactory()
    view = UserSearchView.as_view()

    request = factory.get("/search/", {"q": "pa"})
    force_authenticate(request, user=user_1)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    response.render()
    data = json.loads(response.content)
    assert "results" in data
    assert len(data["results"]) == 8
