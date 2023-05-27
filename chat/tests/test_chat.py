import json

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import DateTimeField
from rest_framework.test import APIClient

from chat.models import ChatGroup, ChatMessage
from chatter.asgi import application
from chatter.utils import EventName, get_group_name


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestChatConsumer:
    async def test_with_anonymous_user(self, origin_header):
        token = "invalid_jwt_access_token"
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat?token={token}",
            headers=[origin_header],
        )

        connected, _ = await communicator.connect()
        assert connected is False, "Should not allow unauthenticated users."

        # NOTE: Even though the connection should fail, warnings will appear if this
        # line is not included.
        await communicator.disconnect()

    async def test_on_connect(self, communicator1_without_handling, user_1):
        connected, _ = await communicator1_without_handling.connect()
        assert connected

        chat_group = await ChatGroup.objects.aget(owner=user_1, name="Precursors rule")
        channel_layer = get_channel_layer()
        assert channel_layer is not None
        await channel_layer.group_send(
            get_group_name(chat_group.pk),
            {
                "type": "handle_create_message",
            },
        )

        response = await communicator1_without_handling.receive_json_from()
        assert response["event_type"] == str(EventName.GROUP_MESSAGE)

        await communicator1_without_handling.disconnect()


@pytest.mark.django_db
def test_create_chat_group(user_1):
    client = APIClient()
    client.force_authenticate(user_1)
    name = "Lo Wang Fan Club"
    response = client.post("/api/chats/", {"owner": user_1.id, "name": name})
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_201_CREATED

    manager = ChatGroup.objects.filter(name=name)
    assert manager.exists()
    chat_group = manager[0]
    assert (
        chat_group.members.count() == 1
    ), "Owner should also be a member of their chat group."

    response.render()
    content = json.loads(response.content)
    assert content["id"] == chat_group.pk


@pytest.mark.django_db
def test_retreive_chat_group(user_1):
    client = APIClient()
    client.force_authenticate(user_1)

    chat_group = ChatGroup.objects.get(name="Precursors rule")
    response = client.get(f"/api/chats/{chat_group.pk}/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == dict
    assert "id" in data
    assert data["owner"]["id"] == user_1.id
    assert data["owner"]["username"] == user_1.username

    for member in data["members"]:
        manager = chat_group.members.filter(id=member["id"])
        assert manager.exists()
        member_model = manager[0]
        assert "username" in member and member["username"] == member_model.username

    for message in data["messages"]:
        manager = ChatMessage.objects.filter(id=message["id"])
        assert manager.exists()
        message_model = manager[0]
        assert message["id"] == message_model.pk
        assert message["user"] == user_1.id
        assert message["message"] == message_model.message
        created = DateTimeField().to_representation(message_model.created)
        assert message["created"] == created


@pytest.mark.django_db
def test_list_chat_group(user_drek, user_1):
    client = APIClient()
    client.force_authenticate(user_drek)

    response = client.get("/api/chats/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 1
    assert data[0]["name"] == "Precursors rule"
    assert data[0]["owner"]["id"] == user_1.id
    assert data[0]["owner"]["username"] == user_1.username


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_destroy_chat_group(user_1, communicator_drek):
    client = APIClient()
    client.force_authenticate(user_1)

    chat_group = await ChatGroup.objects.aget(name="Precursors rule")
    response = await database_sync_to_async(client.delete)(
        f"/api/chats/{chat_group.pk}/"
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    ws_event = await communicator_drek.receive_json_from()
    assert ws_event["event_type"] == str(EventName.GROUP_DESTROY)
    assert "id" in ws_event["message"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_destroy_non_existent_chat_group(user_1):
    client = APIClient()
    client.force_authenticate(user_1)

    response = await database_sync_to_async(client.delete)("/api/chats/12345/")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_destroy_chat_group_user_doesnt_own(user_1, user_drek):
    client = APIClient()
    client.force_authenticate(user_1)

    dreks_chat_group = await ChatGroup.objects.acreate(
        owner=user_drek, name="Long Live the Blarg"
    )
    response = await database_sync_to_async(client.delete)(
        f"/api/chats/{dreks_chat_group.pk}/"
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestChatGroupMemberViewSet:
    async def test_create(self, user_1, user_drek, communicator_drek):
        client = APIClient()
        client.force_authenticate(user_1)

        chat_group = await ChatGroup.objects.aget(
            owner=user_1, name="The Glory Of Panau"
        )
        response = await database_sync_to_async(client.post)(
            f"/api/chats/{chat_group.pk}/members/",
            {"id": user_drek.id},
        )
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_201_CREATED

        ws_event = await communicator_drek.receive_json_from()
        assert ws_event["event_type"] == str(EventName.GROUP_ADD)

        msg = ws_event["message"]
        assert msg["chat_group"] == chat_group.pk
        assert msg["member"]["id"] == user_drek.id
        assert msg["member"]["username"] == user_drek.username

    async def test_destroy(self, user_1, user_drek, communicator_drek):
        client = APIClient()
        client.force_authenticate(user_1)

        chat_group = await ChatGroup.objects.aget(owner=user_1, name="Precursors rule")
        response = await database_sync_to_async(client.delete)(
            f"/api/chats/{chat_group.pk}/members/{user_drek.id}/",
        )
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await chat_group.members.acount() == 1

        ws_event = await communicator_drek.receive_json_from()
        assert ws_event["event_type"] == str(EventName.GROUP_REMOVE)

        msg = ws_event["message"]
        assert msg["chat_group"] == chat_group.pk
        assert msg["member"]["id"] == user_drek.id
        assert msg["member"]["username"] == user_drek.username


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestChatMessageViewSet:
    async def test_create(self, user_1, communicator_drek):
        client = APIClient()
        client.force_authenticate(user_1)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        my_message = "Who were they again??"
        response = await database_sync_to_async(client.post)(
            f"/api/chats/{chat_group.pk}/messages/",
            {
                "message": my_message,
            },
        )
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_201_CREATED

        ws_event = await communicator_drek.receive_json_from()
        assert ws_event["event_type"] == str(EventName.GROUP_MESSAGE)

        msg = ws_event["message"]
        assert type(msg) == dict
        assert msg["user"] == user_1.id
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == my_message
        assert "created" in msg

    async def test_partial_update(self, user_1, communicator1, communicator_drek):
        client = APIClient()
        client.force_authenticate(user_1)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        text = "If Al can't fix it, it's not broke"
        message = await ChatMessage.objects.acreate(
            user=user_1, chat_group=chat_group, message=text
        )

        new_text = "Meet me at my headquarters..."
        response = await database_sync_to_async(client.patch)(
            f"/api/chats/{chat_group.pk}/messages/{message.pk}/",
            {"message": new_text},
        )
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_200_OK

        ws_event = await communicator1.receive_json_from()
        assert ws_event["event_type"] == str(EventName.GROUP_MESSAGE_UPDATE)
        msg = ws_event["message"]
        assert type(msg) == dict
        assert msg["user"] == user_1.id
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == new_text
        assert "created" in msg

        ws_event = await communicator_drek.receive_json_from()
        assert ws_event["event_type"] == str(EventName.GROUP_MESSAGE_UPDATE)
        msg = ws_event["message"]
        assert type(msg) == dict
        assert msg["user"] == user_1.id
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == new_text
        assert "created" in msg
