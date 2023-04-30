import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from chat.models import ChatGroup
from chat.utils import EventName
from chatter.asgi import application
from chatter.utils import get_group_name

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

        # NOTE: Even though the connection should fail, warnings will appear if this
        # line is not included.
        await communicator.disconnect()

    async def test_on_connect(self, communicator1_without_handling, user_1):
        connected, _ = await communicator1_without_handling.connect()
        assert connected

        chat_group = await ChatGroup.objects.aget(owner=user_1, name="Precursors rule")
        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            get_group_name(chat_group.pk),
            {
                "type": "handle_create_message",
                "from_user": user_1.id,
                "from_chat_group": chat_group.pk,
                "message": "Hello world!",
            },
        )

        response = await communicator1_without_handling.receive_json_from()
        assert response["event_type"] == str(EventName.GROUP_MESSAGE)

        await communicator1_without_handling.disconnect()

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
