from channels.generic.websocket import JsonWebsocketConsumer

from chat.models import ChatGroup
from chat.serializers import CreateChatGroupSerializer


class ChatConsumer(JsonWebsocketConsumer):
    """
    The main consumer to handle events relating to:
    - Chat groups
    - Messaging

    It contains custom events that are sent between
    client, server, and channel layer. The following
    represent the custom event names:
    - group:create      Create a chat group for the given user
    """

    def connect(self):
        user = self.scope["user"]

        if not user.is_anonymous:
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        pass

    def receive_json(self, content):
        user = self.scope["user"]
        event_type = content["event_type"]
        message = content["message"]

        if event_type == "group:create":
            serializer = CreateChatGroupSerializer(data=message)

            if not serializer.is_valid():
                self.send_err_event_to_client("serialization")
            else:
                data = serializer.data

                # Create a new chat group for this user.
                new_chat_group = ChatGroup.objects.create(owner=user, name=data["name"])
                # Add user as a member of their chat group.
                new_chat_group.members.add(user)
                new_chat_group.save()

                self.send_event_to_client(
                    "group:created",
                    {
                        "chat_group_id": new_chat_group.pk,
                        "name": new_chat_group.name,
                    },
                )

    def send_event_to_client(self, event_type: str, message):
        self.send_json({"event_type": event_type, "message": message})

    def send_err_event_to_client(self, err_type: str):
        self.send_json({"event_type": "error", "error_type": err_type})
