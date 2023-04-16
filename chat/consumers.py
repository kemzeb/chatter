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
    - group:list        List the user's chat groups they are in
    """

    def connect(self):
        user = self.scope["user"]

        if not user.is_anonymous:
            self.accept()
        else:
            self.close()

    def disconnect(self, close_code):
        pass

    # FIXME: Introduce an abstraction to handle these events. As more events are added,
    # this method will be given more and more reasons to change.
    def receive_json(self, content):
        user = self.scope["user"]
        event_type = content["event_type"]

        if event_type == "group:create":
            message = content["message"]
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
        elif event_type == "group:list":
            chat_groups = ChatGroup.objects.filter(members__id=user.id)
            chat_group_list = []

            for chat_group in chat_groups:
                chat_group_list.append(
                    {
                        "owner_id": chat_group.owner.id,
                        "chat_group_id": chat_group.pk,
                        "name": chat_group.name,
                    }
                )

            # FIXME: When we introduce channel layers, we need to ponder how the user
            # gets notified of new messages.
            self.send_event_to_client("group:listed", chat_group_list)

    def send_event_to_client(self, event_type: str, message):
        self.send_json({"event_type": event_type, "message": message})

    def send_err_event_to_client(self, err_type: str):
        self.send_json({"event_type": "error", "error_type": err_type})
