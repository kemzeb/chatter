import json

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import DateTimeField
from rest_framework.test import APIClient

from chat import serializers
from chat.models import ChatGroup, ChatGroupMembership, ChatMessage
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

    async def test_on_connect(self, communicator_main_without_handling, user_main):
        connected, _ = await communicator_main_without_handling.connect()
        assert connected

        chat_group = await ChatGroup.objects.aget(
            owner=user_main, name="Precursors rule"
        )
        channel_layer = get_channel_layer()
        assert channel_layer is not None
        await channel_layer.group_send(
            get_group_name(chat_group.pk),
            {
                "type": "handle_create_message",
            },
        )

        response = await communicator_main_without_handling.receive_json_from()
        assert response["event_type"] == str(EventName.GROUP_MESSAGE)

        await communicator_main_without_handling.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_chat_group(user_main, communicator_main):
    client = APIClient()
    client.force_authenticate(user_main)
    name = "Lo Wang Fan Club"
    response = await database_sync_to_async(client.post)(
        "/api/chats/", {"owner": user_main.id, "name": name}
    )

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_201_CREATED

    chat_group = await ChatGroup.objects.aget(name=name)
    assert (
        await chat_group.members.acount() == 1
    ), "Owner should also be a member of their chat group."

    response.render()
    content = json.loads(response.content)
    assert content["id"] == chat_group.pk
    serializer = serializers.ChatGroupDetailSerializer(data=content)
    assert serializer.is_valid()

    # Make sure we have created a Channels Group by creating a chat message.
    my_message = "Who were they again??"
    response = await database_sync_to_async(client.post)(
        f"/api/chats/{chat_group.pk}/messages/",
        {
            "message": my_message,
        },
    )
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_201_CREATED

    event = await communicator_main.receive_json_from()
    assert event["event_type"] == EventName.GROUP_MESSAGE


@pytest.mark.django_db
def test_retreive_chat_group(user_main):
    client = APIClient()
    client.force_authenticate(user_main)

    chat_group = ChatGroup.objects.get(name="Precursors rule")
    response = client.get(f"/api/chats/{chat_group.pk}/")

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == dict
    assert data["id"] == chat_group.pk
    assert data["name"] == chat_group.name
    assert data["owner"]["id"] == user_main.id
    assert data["owner"]["username"] == user_main.username


@pytest.mark.django_db
def test_list_chat_group(user_drek, user_main):
    client = APIClient()
    client.force_authenticate(user_drek)

    response = client.get("/api/chats/")

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)
    assert type(data) == list
    assert len(data) == 1
    assert "id" in data[0]
    assert data[0]["name"] == "Precursors rule"
    assert data[0]["owner"]["id"] == user_main.id
    assert data[0]["owner"]["username"] == user_main.username


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_destroy_chat_group(user_main, communicator_main, communicator_drek):
    client = APIClient()
    client.force_authenticate(user_main)

    chat_group = await ChatGroup.objects.aget(name="Precursors rule")
    response = await database_sync_to_async(client.delete)(
        f"/api/chats/{chat_group.pk}/"
    )

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    event = await communicator_main.receive_json_from()
    assert event["event_type"] == str(EventName.GROUP_DESTROY)
    assert "id" in event["message"]

    event = await communicator_drek.receive_json_from()
    assert event["event_type"] == str(EventName.GROUP_DESTROY)
    assert "id" in event["message"]


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_destroy_non_existent_chat_group(user_main):
    client = APIClient()
    client.force_authenticate(user_main)

    response = await database_sync_to_async(client.delete)("/api/chats/12345/")

    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_destroy_chat_group_user_doesnt_own(user_main, user_drek):
    client = APIClient()
    client.force_authenticate(user_main)

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
    async def test_create(
        self, user_main, user_drek, communicator_main, communicator_drek
    ):
        client = APIClient()
        client.force_authenticate(user_main)
        chat_group = await ChatGroup.objects.aget(
            owner=user_main, name="The Glory Of Panau"
        )
        response = await database_sync_to_async(client.post)(
            f"/api/chats/{chat_group.pk}/members/",
            {"id": user_drek.id},
        )

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_201_CREATED
        member = await database_sync_to_async(ChatGroupMembership.objects.filter)(
            chat_group=chat_group.pk, user=user_drek.id
        )
        assert await member.aexists()

        event = await communicator_main.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_ADD)
        msg = event["message"]
        assert msg["chat_group"] == chat_group.pk
        assert msg["user"]["id"] == user_drek.id
        assert msg["user"]["username"] == user_drek.username

        event = await communicator_drek.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_ADD)
        msg = event["message"]
        assert msg["chat_group"] == chat_group.pk
        assert msg["user"]["id"] == user_drek.id
        assert msg["user"]["username"] == user_drek.username

    async def test_list_ensure_sorted_ascending_and_valid(self, user_main, user_drek):
        client = APIClient()
        client.force_authenticate(user_main)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")

        response = await database_sync_to_async(client.get)(
            f"/api/chats/{chat_group.pk}/members/",
        )

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_200_OK
        response.render()
        data = json.loads(response.content)
        assert isinstance(data, list)

        assert len(data) > 0
        assert data[0]["user"]["id"] == user_drek.id

        for member in data:
            serializer = serializers.ChatGroupMemberSerializer(data=member)
            assert await database_sync_to_async(serializer.is_valid)()

    @pytest.mark.usefixtures("user_main")
    async def test_list_non_member(self, user_2):
        client = APIClient()
        client.force_authenticate(user_2)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        response = await database_sync_to_async(client.get)(
            f"/api/chats/{chat_group.pk}/members/",
        )

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_destroy(
        self, user_main, user_drek, communicator_main, communicator_drek
    ):
        client = APIClient()
        client.force_authenticate(user_main)

        chat_group = await ChatGroup.objects.aget(
            owner=user_main, name="Precursors rule"
        )
        response = await database_sync_to_async(client.delete)(
            f"/api/chats/{chat_group.pk}/members/{user_drek.id}/",
        )

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await chat_group.members.acount() == 1

        event = await communicator_main.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_REMOVE)
        msg = event["message"]
        assert msg["chat_group"] == chat_group.pk
        assert msg["user"]["id"] == user_drek.id
        assert msg["user"]["username"] == user_drek.username

        event = await communicator_drek.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_REMOVE)
        msg = event["message"]
        assert msg["chat_group"] == chat_group.pk
        assert msg["user"]["id"] == user_drek.id
        assert msg["user"]["username"] == user_drek.username


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
class TestChatMessageViewSet:
    async def test_create(self, user_main, communicator_main, communicator_drek):
        client = APIClient()
        client.force_authenticate(user_main)

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

        event = await communicator_main.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_MESSAGE)
        msg = event["message"]
        assert type(msg) == dict
        assert msg["user"]["id"] == user_main.id
        assert msg["user"]["username"] == user_main.username
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == my_message
        assert "created" in msg

        event = await communicator_drek.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_MESSAGE)
        msg = event["message"]
        assert type(msg) == dict
        assert msg["user"]["id"] == user_main.id
        assert msg["user"]["username"] == user_main.username
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == my_message
        assert "created" in msg

    async def test_partial_update(
        self, user_main, communicator_main, communicator_drek
    ):
        client = APIClient()
        client.force_authenticate(user_main)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        text = "If Al can't fix it, it's not broke"
        message = await ChatMessage.objects.acreate(
            user=user_main, chat_group=chat_group, message=text
        )

        new_text = "Meet me at my headquarters..."
        response = await database_sync_to_async(client.patch)(
            f"/api/chats/{chat_group.pk}/messages/{message.pk}/",
            {"message": new_text},
        )

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_200_OK

        event = await communicator_main.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_MESSAGE_UPDATE)
        msg = event["message"]
        assert type(msg) == dict
        assert msg["user"]["id"] == user_main.id
        assert msg["user"]["username"] == user_main.username
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == new_text
        assert "created" in msg

        event = await communicator_drek.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_MESSAGE_UPDATE)
        msg = event["message"]
        assert type(msg) == dict
        assert msg["user"]["id"] == user_main.id
        assert msg["user"]["username"] == user_main.username
        assert msg["chat_group"] == chat_group.pk
        assert msg["message"] == new_text
        assert "created" in msg

    async def test_list_existing_member(self, user_main):
        client = APIClient()
        client.force_authenticate(user_main)

        chat_group = await ChatGroup.objects.aget(
            owner=user_main, name="Precursors rule"
        )
        recent_message = await ChatMessage.objects.acreate(
            user=user_main, chat_group=chat_group, message="A chat message"
        )
        response = await database_sync_to_async(client.get)(
            f"/api/chats/{chat_group.pk}/messages/",
        )
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_200_OK
        response.render()
        data = json.loads(response.content)
        assert isinstance(data, list) and len(data) == 3

        # Make sure that the most recent message is at the bottom.
        assert data[-1]["id"] == recent_message.pk

        for message in data:
            msg_obj = await ChatMessage.objects.aget(id=message["id"])
            assert message["id"] == msg_obj.pk
            assert message["user"]["id"] == user_main.id
            assert message["user"]["username"] == user_main.username
            assert message["message"] == msg_obj.message
            created = DateTimeField().to_representation(msg_obj.created)
            assert message["created"] == created

    @pytest.mark.usefixtures("user_main")
    async def test_list_non_member(self, user_2):
        client = APIClient()
        client.force_authenticate(user_2)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        response = await database_sync_to_async(client.get)(
            f"/api/chats/{chat_group.pk}/messages/",
        )
        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_destroy(self, user_main, communicator_main, communicator_drek):
        client = APIClient()
        client.force_authenticate(user_main)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        message = await ChatMessage.objects.acreate(
            user=user_main,
            chat_group=chat_group,
            message="How could I have known she was your sister",
        )
        message_id = message.pk
        response = await database_sync_to_async(client.delete)(
            f"/api/chats/{chat_group.pk}/messages/{message.pk}/"
        )

        assert isinstance(response, Response)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert await chat_group.messages.acount() == 2

        event = await communicator_main.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_MESSAGE_DELETE)
        msg = event["message"]
        assert type(msg) == dict
        assert msg["chat_group"] == chat_group.pk

        event = await communicator_drek.receive_json_from()
        assert event["event_type"] == str(EventName.GROUP_MESSAGE_DELETE)
        msg = event["message"]
        assert type(msg) == dict
        assert msg["id"] == message_id
        assert msg["chat_group"] == chat_group.pk
