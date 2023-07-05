import json

import pytest
from channels.db import database_sync_to_async
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient

from chatter.utils import EventName
from users.models import FriendRequest


@pytest.mark.django_db
@pytest.mark.usefixtures("add_multiple_users")
def test_friends_search_view(user_main):
    client = APIClient()
    client.force_authenticate(user_main)

    response = client.get("/api/users/me/friends/search/", {"q": "pa"})
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert len(data["results"]) == 8


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_delete_friend_view(
    user_main, user_drek, communicator_main, communicator_drek
):
    client = APIClient()
    client.force_authenticate(user_main)

    await user_main.friends.aadd(user_drek)

    response = await database_sync_to_async(client.delete)(
        f"/api/users/me/friends/{user_drek.id}/"
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert await user_main.friends.acount() == 2

    event = await communicator_main.receive_json_from()
    assert event["event_type"] == str(EventName.USER_UNFRIEND)
    msg = event["message"]
    assert msg["id"] == user_drek.id
    assert msg["username"] == user_drek.username

    event = await communicator_drek.receive_json_from()
    assert event["event_type"] == str(EventName.USER_UNFRIEND)
    msg = event["message"]
    assert msg["id"] == user_main.id
    assert msg["username"] == user_main.username


@pytest.mark.django_db
def test_list_friends_view(user_main):
    client = APIClient()
    client.force_authenticate(user_main)

    response = client.get("/api/users/me/friends/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 2


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_friend_request(user_main, user_drek, communicator_drek):
    client = APIClient()
    client.force_authenticate(user_main)

    response = await database_sync_to_async(client.post)(
        "/api/users/me/friendrequests/", {"username": user_drek.username}
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_201_CREATED

    response.render()
    data = json.loads(response.content)
    assert "id" in data

    event = await communicator_drek.receive_json_from()
    assert event["event_type"] == str(EventName.USER_FRIEND_REQUEST)
    msg = event["message"]
    assert "id" in msg
    assert msg["requester"]["id"] == user_main.id
    assert msg["requester"]["username"] == user_main.username
    assert msg["addressee"]["id"] == user_drek.id
    assert msg["addressee"]["username"] == user_drek.username


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_accept_friend_request(
    user_main, user_drek, communicator_main, communicator_drek
):
    client = APIClient()
    client.force_authenticate(user_main)

    friend_request = await FriendRequest.objects.acreate(
        requester=user_drek, addressee=user_main
    )

    response = await database_sync_to_async(client.delete)(
        f"/api/users/me/friendrequests/{friend_request.pk}/?accept=1"
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await FriendRequest.objects.acontains(friend_request)
    assert await user_drek.friends.acontains(user_main)

    event = await communicator_drek.receive_json_from()
    assert event["event_type"] == str(EventName.USER_ACCEPT_FRIEND_REQUEST)
    msg = event["message"]
    assert "id" in msg
    assert msg["requester"]["id"] == user_drek.id
    assert msg["requester"]["username"] == user_drek.username
    assert msg["addressee"]["id"] == user_main.id
    assert msg["addressee"]["username"] == user_main.username

    event = await communicator_main.receive_json_from()
    assert event["event_type"] == str(EventName.USER_ACCEPT_FRIEND_REQUEST)
    msg = event["message"]
    assert "id" in msg
    assert msg["requester"]["id"] == user_drek.id
    assert msg["requester"]["username"] == user_drek.username
    assert msg["addressee"]["id"] == user_main.id
    assert msg["addressee"]["username"] == user_main.username


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_reject_friend_request(
    user_main, user_drek, communicator_main, communicator_drek
):
    client = APIClient()
    client.force_authenticate(user_main)

    friend_request = await FriendRequest.objects.acreate(
        requester=user_drek, addressee=user_main
    )

    response = await database_sync_to_async(client.delete)(
        f"/api/users/me/friendrequests/{friend_request.pk}/?accept=0"
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not await FriendRequest.objects.acontains(friend_request)
    assert not await user_drek.friends.acontains(user_main)

    event = await communicator_drek.receive_json_from()
    assert event["event_type"] == str(EventName.USER_REJECT_FRIEND_REQUEST)
    msg = event["message"]
    assert "id" in msg
    assert msg["requester"]["id"] == user_drek.id
    assert msg["requester"]["username"] == user_drek.username
    assert msg["addressee"]["id"] == user_main.id
    assert msg["addressee"]["username"] == user_main.username

    event = await communicator_main.receive_json_from()
    assert event["event_type"] == str(EventName.USER_REJECT_FRIEND_REQUEST)
    msg = event["message"]
    assert "id" in msg
    assert msg["requester"]["id"] == user_drek.id
    assert msg["requester"]["username"] == user_drek.username
    assert msg["addressee"]["id"] == user_main.id
    assert msg["addressee"]["username"] == user_main.username


@pytest.mark.django_db
def test_list_friend_request(user_main, user_drek):
    client = APIClient()
    client.force_authenticate(user_main)

    FriendRequest.objects.create(requester=user_drek, addressee=user_main)

    response = client.get("/api/users/me/friendrequests/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 1
    assert "id" in data[0]
    assert data[0]["requester"]["id"] == user_drek.id
    assert data[0]["requester"]["username"] == user_drek.username
