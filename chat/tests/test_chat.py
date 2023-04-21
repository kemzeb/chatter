import json

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from chat.models import ChatGroup, ChatMessage
from chatter.asgi import application


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

        await communicator.disconnect()

    async def test_on_connect(self, communicator1_without_handling, user_1):
        connected, _ = await communicator1_without_handling.connect()
        assert connected

        response = await communicator1_without_handling.receive_from()
        response = json.loads(response)

        assert "event_type" in response
        assert response["event_type"] == "group:connect"

        assert "message" in response
        chat_groups = response["message"]
        assert type(chat_groups) == list
        assert len(chat_groups) == 2

        for group in chat_groups:
            assert "owner_id" in group and group["owner_id"] == user_1.id
            assert "chat_group_id" in group

            manager = await database_sync_to_async(ChatGroup.objects.filter)(
                id=group["chat_group_id"]
            )
            group_model = await manager.afirst()
            assert group_model
            assert group["name"] == group_model.name

        channel_layer = get_channel_layer()

        a_chat_group_id = chat_groups[0]["chat_group_id"]
        await channel_layer.group_send(
            f"chat_{a_chat_group_id}",
            {
                "type": "handle_chat_message",
                "message": "Hello world!",
            },
        )

        group_msg = await communicator1_without_handling.receive_from()
        group_msg = json.loads(group_msg)
        assert "message" in group_msg

        await communicator1_without_handling.disconnect()

    async def test_event_group_create(self, communicator1):
        name = "Veldin rocks"
        await communicator1.send_json_to(
            {"event_type": "group:create", "message": {"name": name}}
        )
        response = await communicator1.receive_from()
        response = json.loads(response)

        assert "event_type" in response and response["event_type"] == "group:create"

        assert "message" in response
        msg = response["message"]
        assert "chat_group_id" in msg and type(msg["chat_group_id"]) == int
        assert "name" in msg and msg["name"] == name

        id = msg["chat_group_id"]
        chat_group_manager = await database_sync_to_async(ChatGroup.objects.filter)(
            id=id
        )
        assert await chat_group_manager.aexists()

        new_chat_group = await chat_group_manager.afirst()
        membership_row_count = await new_chat_group.members.acount()
        assert (
            membership_row_count == 1
        ), "Owner should be a member of their chat group."

    async def test_event_group_fetch(self, communicator1, user_1):
        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        await communicator1.send_json_to(
            {"event_type": "group:fetch", "message": {"chat_group_id": chat_group.pk}}
        )

        response = await communicator1.receive_from()
        response = json.loads(response)

        assert response["event_type"] == "group:fetch"

        msg = response["message"]

        assert "members" in msg
        assert type(msg["members"]) == list

        for member in msg["members"]:
            manager = await database_sync_to_async(chat_group.members.filter)(
                id=member["id"]
            )
            member_model = await manager.afirst()
            assert member_model
            assert "username" in member and member["username"] == member_model.username

        assert "messages" in msg
        assert type(msg["messages"]) == list

        for message in msg["messages"]:
            manager = await database_sync_to_async(ChatMessage.objects.filter)(
                id=message["id"]
            )
            message_model = await manager.afirst()
            assert message_model
            assert "user_id" in message and message["user_id"] == user_1.id
            assert "message" in message and message["message"] == message_model.message
            assert "sent_on" in message
            assert message["sent_on"] == str(message_model.sent_on)

    async def test_event_group_message(self, communicator1, user_1):
        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        my_message = "Need to drown my sorrows in dark eco."
        await communicator1.send_json_to(
            {
                "event_type": "group:message",
                "message": {
                    "from_chat_group": chat_group.pk,
                    "message": my_message,
                },
            }
        )

        response = await communicator1.receive_from()
        response = json.loads(response)

        assert "event_type" in response
        assert response["event_type"] == "group:message"

        assert "message" in response
        msg = response["message"]
        assert type(msg) == dict
        assert msg["from_user"] == user_1.id
        assert msg["from_chat_group"] == chat_group.pk
        assert msg["message"] == my_message
        assert "sent_on" in msg
