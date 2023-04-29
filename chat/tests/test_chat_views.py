import json

import pytest
from channels.db import database_sync_to_async
from django.http import HttpResponse
from django.test import RequestFactory
from rest_framework import status
from rest_framework.serializers import DateTimeField
from rest_framework.test import force_authenticate

from chat import views
from chat.models import ChatGroup, ChatMessage
from chat.utils import EventName


@pytest.mark.django_db
def test_create_chat_group(user_1):
    factory = RequestFactory()
    view = views.CreateChatGroup.as_view()
    name = "Lo Wang Fan Club"
    request = factory.post("/api/chat/chatgroups/", {"owner": user_1.id, "name": name})
    force_authenticate(request, user=user_1)
    response = view(request)

    assert response.status_code == status.HTTP_201_CREATED

    manager = ChatGroup.objects.filter(name=name)
    assert manager.exists()
    chat_group = manager[0]

    assert (
        chat_group.members.count() == 1
    ), "Owner should also be a member of their chat group."

    response.render()
    content = json.loads(response.content)
    assert content["id"] == chat_group.pk


@pytest.mark.django_db
def test_chat_group_detail(user_1):
    factory = RequestFactory()
    view = views.ChatGroupDetail.as_view()
    chat_group = ChatGroup.objects.get(name="Precursors rule")

    request = factory.get(f"/api/chat/chatgroups/{chat_group.pk}/")
    force_authenticate(request, user=user_1)
    response = view(request, pk=chat_group.pk)

    assert response.status_code == status.HTTP_200_OK

    response.render()
    data = json.loads(response.content)

    assert type(data) == dict
    assert "id" in data
    assert data["owner"]["id"] == user_1.id
    assert data["owner"]["username"] == user_1.username

    for member in data["members"]:
        manager = chat_group.members.filter(id=member["id"])
        assert manager.exists()
        member_model = manager[0]
        assert "username" in member and member["username"] == member_model.username

    for message in data["messages"]:
        manager = ChatMessage.objects.filter(id=message["id"])
        assert manager.exists()
        message_model = manager[0]
        assert message["id"] == message_model.pk
        assert message["from_user"] == user_1.id
        assert message["message"] == message_model.message
        model_sent_on = DateTimeField().to_representation(message_model.sent_on)
        assert message["sent_on"] == model_sent_on


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_create_chat_message(user_1, communicator_drek):
    factory = RequestFactory()
    view = views.CreateChatMessage.as_view()
    chat_group = await ChatGroup.objects.aget(name="Precursors rule")
    my_message = "Who were they again??"

    request = factory.post(
        "/api/chat/messages/",
        {
            "from_user": user_1.id,
            "from_chat_group": chat_group.pk,
            "message": my_message,
        },
    )
    force_authenticate(request, user=user_1)
    response: HttpResponse = await database_sync_to_async(view)(request)
    assert response.status_code == status.HTTP_201_CREATED

    ws_event = await communicator_drek.receive_json_from()
    assert ws_event["event_type"] == str(EventName.GROUP_MESSAGE)

    msg = ws_event["message"]
    assert type(msg) == dict
    assert msg["from_user"] == user_1.id
    assert msg["from_chat_group"] == chat_group.pk
    assert msg["message"] == my_message
    assert "sent_on" in msg
