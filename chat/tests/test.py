import json

import pytest
from channels.testing import WebsocketCommunicator

from chatter.asgi import application


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer_with_authenticated_user(communicator_user_1):
    connected, _ = await communicator_user_1.connect()
    assert connected, "Should allow authenticated users."

    await communicator_user_1.disconnect()


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
    connected, _ = await communicator_user_1.connect()
    assert connected

    await communicator_user_1.send_json_to(
        {"event_type": "group:create", "message": {"name": "Veldin rocks"}}
    )
    response = await communicator_user_1.receive_from()
    response = json.loads(response)

    assert response["event_type"] == "group:created"

    # FIXME: Figure out how to test DB with async code without errors.

    await communicator_user_1.disconnect()
