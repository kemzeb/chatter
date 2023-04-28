import json

import pytest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.test import force_authenticate

from chat.models import ChatGroup
from chat.views import CreateChatGroup


@pytest.mark.django_db
def test_create_chat_group(user_1):
    factory = RequestFactory()
    view = CreateChatGroup.as_view()
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
    assert "id" in content and content["id"] == chat_group.pk
