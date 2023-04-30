import json

import pytest
from channels.db import database_sync_to_async
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import force_authenticate

from users import views


@pytest.mark.django_db
def test_friends_list_view(user_1):
    factory = RequestFactory()
    view = views.FriendsListView.as_view()

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
    view = views.UserSearchView.as_view()

    request = factory.get("/search/", {"q": "pa"})
    force_authenticate(request, user=user_1)
    response = view(request)

    assert response.status_code == status.HTTP_200_OK
    response.render()
    data = json.loads(response.content)
    assert "results" in data
    assert len(data["results"]) == 8


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_friend_request(user_1, user_drek, communicator_drek):
    factory = RequestFactory()
    view = views.FriendRequestView.as_view()

    request = factory.post("/friendrequests/", {"addressee": user_drek.id})
    force_authenticate(request, user=user_1)
    response: HttpResponse = await database_sync_to_async(view)(request)

    assert response.status_code == status.HTTP_201_CREATED

    response.render()
    data = json.loads(response.content)
    assert "id" in data

    ws_event = await communicator_drek.receive_json_from()
    assert ws_event["event_type"] == "user:friendrequest"
    msg = ws_event["message"]
    assert msg["requester"] == user_1.id
    assert msg["addressee"] == user_drek.id
    assert "id" in msg
