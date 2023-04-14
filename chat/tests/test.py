import json

import pytest
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
async def test_chat_consumer_with_event_group_create(communicator_user_1):
    name = "Veldin rocks"
    await communicator_user_1.send_json_to(
        {"event_type": "group:create", "message": {"name": name}}
    )

    response = await communicator_user_1.receive_from()
    response = json.loads(response)
    msg = response["message"]
    assert response["event_type"] == "group:created"
    assert "chat_group_id" in msg
    assert type(msg["chat_group_id"]) == int
    assert "name" in msg
    assert msg["name"] == name

    id = msg["chat_group_id"]
    new_chat_group = await ChatGroup.objects.aget(id=id)
    assert new_chat_group is not None

    membership_row_count = await new_chat_group.members.acount()
    assert membership_row_count == 1, "Owner should be a member of their chat group."
