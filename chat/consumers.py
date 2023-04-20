from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chat.models import ChatGroup, ChatMessage
from chat.serializers import (
    CreateChatGroupSerializer,
    FetchChatGroupSerializer,
    MessageChatGroupSerializer,
)


class ChatConsumer(JsonWebsocketConsumer):
    """
    The main consumer to handle events relating to:
    - Chat groups
    - Messaging

    It contains custom events that are sent between
    client, server, and channel layer. The following
    represent the custom event names:
    - group:create      Create a chat group for the given user
    - group:fetch       Fetches members and messages of a chat group
    - group:message     Receive client messages and send to named group
    """

    def connect(self):
        user = self.scope["user"]

        if not user.is_anonymous:
            chat_groups = ChatGroup.objects.filter(members__id=user.id)
            chat_group_list = []

            self.accept()

            for chat_group in chat_groups:
                chat_group_list.append(
                    {
                        "owner_id": chat_group.owner.id,
                        "chat_group_id": chat_group.pk,
                        "name": chat_group.name,
                    }
                )
                async_to_sync(self.channel_layer.group_add)(
                    f"chat_{chat_group.pk}", self.channel_name
                )

            self.send_event_to_client("group:connected", chat_group_list)
        else:
            self.close()

    def disconnect(self, close_code):
        user = self.scope["user"]
        chat_groups = ChatGroup.objects.filter(members__id=user.id)

        for chat_group in chat_groups:
            async_to_sync(self.channel_layer.group_discard)(
                f"chat_{chat_group.pk}", self.channel_name
            )

    event_type = {
        "group:create": "create_group_event",
        "group:fetch": "fetch_group_event",
        "group:message": "message_group_event",
    }

    def receive_json(self, content):
        if (
            ("event_type" not in content)
            or ("message" not in content)
            or (content["event_type"] not in self.event_type)
        ):
            self.send_err_event_to_client("bad message")
            return

        getattr(self, self.event_type[content["event_type"]])(content["message"])

    def create_group_event(self, message):
        user = self.scope["user"]
        serializer = CreateChatGroupSerializer(data=message)

        if not serializer.is_valid():
            self.send_err_event_to_client("serialization")
            return

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

    def fetch_group_event(self, message):
        user = self.scope["user"]
        serializer = FetchChatGroupSerializer(data=message)

        if not serializer.is_valid():
            self.send_err_event_to_client("serialization")
            return

        data = serializer.data

        # Make sure the group exists.
        chat_group_manager = ChatGroup.objects.filter(id=data["chat_group_id"])

        if not chat_group_manager.exists():
            self.send_err_event_to_client("forbidden")
            return

        chat_group = chat_group_manager[0]

        # Make sure the user is a member of the group.
        members_manager = chat_group.members.filter(id=user.id)

        if not members_manager.exists():
            self.send_err_event_to_client("forbidden")
            return

        members = [
            {"id": member.id, "username": member.username}
            for member in chat_group.members.all().only("id", "username")
        ]
        messages = [
            {
                "user_id": message.from_user.id,
                "id": message.pk,
                "message": message.message,
                "date_sent": message.date_sent.ctime(),
            }
            for message in ChatMessage.objects.filter(from_chat_group=chat_group).only(
                "from_user", "id", "message", "date_sent"
            )
        ]

        self.send_event_to_client(
            "group:fetched", {"members": members, "messages": messages}
        )

    def message_group_event(self, message):
        user = self.scope["user"]
        serializer = MessageChatGroupSerializer(data=message)

        if not serializer.is_valid():
            self.send_err_event_to_client("serialization")
            return

        data = serializer.data

        # Make sure the group exists.
        chat_group_manager = ChatGroup.objects.filter(id=data["from_chat_group"])

        if not chat_group_manager.exists():
            self.send_err_event_to_client("forbidden")
            return

        chat_group = chat_group_manager[0]

        # Make sure the user is a member of the group.
        members_manager = chat_group.members.filter(id=user.id)

        if not members_manager.exists():
            self.send_err_event_to_client("forbidden")
            return

        new_message = ChatMessage.objects.create(
            from_user=user, from_chat_group=chat_group, message=data["message"]
        )

        async_to_sync(self.channel_layer.group_send)(
            f"chat_{chat_group.pk}",
            {
                "type": "handle_chat_message",
                "from_user": user.id,
                "from_chat_group": chat_group.pk,
                "message": new_message.message,
            },
        )

    def handle_chat_message(self, event):
        self.send_event_to_client("group:messaged", event)

    def send_event_to_client(self, event_type: str, message):
        self.send_json({"event_type": event_type, "message": message})

    def send_err_event_to_client(self, err_type: str):
        self.send_event_to_client("error", err_type)
