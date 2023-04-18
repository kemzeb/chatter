import json

import pytest
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from chat.models import ChatGroup
from chatter.asgi import application


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer_with_anonymous_user(origin_header):
    token = "invalid_jwt_access_token"
    communicator = WebsocketCommunicator(
        application,
        f"/ws/chat?token={token}",
        headers=[origin_header],
    )

    connected, _ = await communicator.connect()
    assert connected is False, "Should not allow unauthenticated users"

    await communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer_on_connect(communicator1, user_1):
    response = await communicator1.receive_from()
    response = json.loads(response)

    assert response["event_type"] == "group:connected"

    assert "message" in response
    chat_groups = response["message"]
    assert type(chat_groups) == list
    assert len(chat_groups) == 2

    for group in chat_groups:
        assert "owner_id" in group
        assert group["owner_id"] == user_1.id
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
            "event_type": "group:message",
            "message": "Hello world!",
        },
    )

    group_msg = await communicator1.receive_from()
    group_msg = json.loads(group_msg)
    assert "event_type" in group_msg


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer_with_event_group_create(communicator1):
    # Ignore the group:connected response.
    await communicator1.receive_from()

    name = "Veldin rocks"
    await communicator1.send_json_to(
        {"event_type": "group:create", "message": {"name": name}}
    )
    response = await communicator1.receive_from()
    response = json.loads(response)

    assert response["event_type"] == "group:created"

    assert "message" in response
    msg = response["message"]
    assert "chat_group_id" in msg
    assert type(msg["chat_group_id"]) == int
    assert "name" in msg
    assert msg["name"] == name

    id = msg["chat_group_id"]
    new_chat_group = await ChatGroup.objects.aget(id=id)
    assert new_chat_group is not None

    membership_row_count = await new_chat_group.members.acount()
    assert membership_row_count == 1, "Owner should be a member of their chat group."
