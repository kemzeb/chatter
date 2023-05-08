import json

import pytest
from channels.db import database_sync_to_async
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from users.models import FriendRequest


@pytest.mark.django_db
def test_friends_list_view(user_1):
    client = APIClient()
    client.force_authenticate(user_1)

    response = client.get("/api/users/me/friends/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 2


@pytest.mark.django_db
@pytest.mark.usefixtures("add_multiple_users")
def test_user_search_view(user_1):
    client = APIClient()
    client.force_authenticate(user_1)

    response = client.get("/search/", {"q": "pa"})
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert "results" in data
    assert len(data["results"]) == 8


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_friend_request(user_1, user_drek, communicator_drek):
    client = APIClient()
    client.force_authenticate(user_1)

    response = await database_sync_to_async(client.post)(
        "/api/users/me/friendrequests/", {"addressee": user_drek.id}
    )
    assert isinstance(response, Response)
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


@pytest.mark.django_db
def test_list_friend_request(user_1, user_drek):
    client = APIClient()
    client.force_authenticate(user_1)

    FriendRequest.objects.create(requester=user_drek, addressee=user_1)

    response = client.get("/api/users/me/friendrequests/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 1
    assert data[0]["requester"] == user_drek.id
    assert data[0]["addressee"] == user_1.id
