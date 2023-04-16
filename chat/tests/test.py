import json

import pytest
from channels.db import database_sync_to_async
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


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer_with_event_group_list(communicator_user_1, user_1):
    name1 = "Precursors rule"
    name2 = "The Glory Of Panau"

    group_1 = await ChatGroup.objects.acreate(owner=user_1, name=name1)
    group_2 = await ChatGroup.objects.acreate(owner=user_1, name=name2)
    await database_sync_to_async(group_1.members.add)(user_1)
    await database_sync_to_async(group_2.members.add)(user_1)

    await communicator_user_1.send_json_to({"event_type": "group:list"})

    response = await communicator_user_1.receive_from()
    response = json.loads(response)

    assert response["event_type"] == "group:listed"

    assert "message" in response
    chat_groups = response["message"]
    assert type(chat_groups) == list
    assert len(chat_groups) == 2

    for group in chat_groups:
        assert "owner_id" in group
        assert group["owner_id"] == user_1.id
        assert "chat_group_id" in group
        assert group["chat_group_id"] in (group_1.pk, group_2.pk)
        assert group["name"] in [name1, name2]
