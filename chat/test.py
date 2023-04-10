import pytest
from channels.testing import WebsocketCommunicator

from chatter.asgi import application


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer(user_created_return_jwt_access_token):
    token = user_created_return_jwt_access_token
    communicator = WebsocketCommunicator(application, f"/ws/chat?token={token}")

    connected, _ = await communicator.connect()
    assert connected

    await communicator.disconnect()
