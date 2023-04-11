import pytest
from channels.testing import WebsocketCommunicator

from chatter.asgi import application


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_chat_consumer(jwt_access_token_of_auth_user, origin_header):
    communicator = WebsocketCommunicator(
        application,
        f"/ws/chat?token={jwt_access_token_of_auth_user}",
        headers=[origin_header],
    )

    connected, _ = await communicator.connect()
    assert connected

    await communicator.disconnect()
