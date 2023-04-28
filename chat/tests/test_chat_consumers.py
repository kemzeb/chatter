import json

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from chat.models import ChatGroup
from chat.utils import EventName
from chatter.asgi import application

# FIXME: These tests need to be much more robust. There are edge cases that are not
# being handled and assertions that don't exist yet but we should be making.


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

        group_msg = await communicator1_without_handling.receive_json_from()
        assert "message" in group_msg

        await communicator1_without_handling.disconnect()

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
        response = await communicator1.receive_json_from()
        assert "event_type" in response
        assert response["event_type"] == "group:message"

        assert "message" in response
        msg = response["message"]
        assert type(msg) == dict
        assert msg["from_user"] == user_1.id
        assert msg["from_chat_group"] == chat_group.pk
        assert msg["message"] == my_message
        assert "sent_on" in msg

    async def test_friend_request(self, communicator1, communicator2, user_2):
        await communicator1.send_json_to(
            {"event_type": "user:friendrequest", "message": {"addressee": user_2.id}}
        )

        response = await communicator1.receive_json_from()
        assert "event_type" in response
        assert response["event_type"] == "user:friendrequest"

        response = await communicator2.receive_json_from()
        assert "event_type" in response
        assert response["event_type"] == "user:friendrequest"

    async def test_group_add(self, communicator1, user_1, communicator2, user_2):
        await database_sync_to_async(user_1.friends.add)(user_2)

        chat_group = await ChatGroup.objects.aget(name="Precursors rule")
        await communicator1.send_json_to(
            {
                "event_type": str(EventName.GROUP_ADD),
                "message": {"chat_group": chat_group.pk, "new_member": user_2.id},
            }
        )

        response = await communicator1.receive_json_from()
        assert "event_type" in response
        assert response["event_type"] == str(EventName.GROUP_ADD)

        response = await communicator2.receive_json_from()
        assert "event_type" in response
        assert response["event_type"] == str(EventName.GROUP_ADD)
