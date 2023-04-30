from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chat import serializers
from chat.models import ChatGroup
from chatter.utils import get_channel_group_name, get_group_name
from users.models import ChatterUser

from .utils import EventErrCode, EventName


class ChatConsumer(JsonWebsocketConsumer):
    """
    The main consumer to handle events relating to:
    - Chat groups
    - New messages
    - Friend requests
    """

    def connect(self):
        user = self.scope["user"]

        if user.is_anonymous:
            self.close()
            return

        chat_groups = ChatGroup.objects.filter(members__id=user.id)
        chat_group_list = []

        self.accept()

        async_to_sync(self.channel_layer.group_add)(
            get_channel_group_name(user.username), self.channel_name
        )

        for chat_group in chat_groups:
            chat_group_list.append(
                {
                    "owner_id": chat_group.owner.id,
                    "chat_group_id": chat_group.pk,
                    "name": chat_group.name,
                }
            )
            async_to_sync(self.channel_layer.group_add)(
                get_group_name(chat_group.pk), self.channel_name
            )

    def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_anonymous:
            return

        async_to_sync(self.channel_layer.group_discard)(
            get_channel_group_name(user.username), self.channel_name
        )

        chat_groups = user.chat_groups.all()
        for chat_group in chat_groups:
            print("YES:", chat_group.pk)
            async_to_sync(self.channel_layer.group_discard)(
                get_group_name(chat_group.pk), self.channel_name
            )

    event_type = {
        str(EventName.GROUP_ADD): "group_add_event",
    }

    def receive_json(self, content):
        if (
            ("event_type" not in content)
            or ("message" not in content)
            or (content["event_type"] not in self.event_type)
        ):
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        getattr(self, self.event_type[content["event_type"]])(content["message"])

    def group_add_event(self, message):
        serializer = serializers.ChatGroupAddUserSerializer(data=message)
        if not serializer.is_valid():
            self.send_err_event_to_client(EventErrCode.SERIALIZATION)
            return

        new_member_id = serializer.data["new_member"]

        # Make sure the user exists.
        user_manager = ChatterUser.objects.filter(id=new_member_id)
        if not user_manager.exists():
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        new_member = user_manager[0]
        user = self.scope["user"]

        # Make sure the user and new member are friends. Otherwise anyone can add you to
        # their chat group!
        if not new_member.friends.filter(id=user.id).exists():
            self.send_err_event_to_client(EventErrCode.FORBIDDEN)
            return

        chat_group_id = serializer.data["chat_group"]

        # Make sure the chat group exists.
        chat_group_manager = ChatGroup.objects.filter(id=chat_group_id)
        if not chat_group_manager.exists():
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        chat_group = chat_group_manager[0]

        # Make sure the user owns the group.
        if chat_group.owner != user:
            self.send_err_event_to_client(EventErrCode.FORBIDDEN)
            return

        chat_group.members.add(new_member)

        message = {
            "owner": user.id,
            "chat_group": chat_group.pk,
            "name": chat_group.name,
        }

        # Send the message to the new member if they have an open channel.
        async_to_sync(self.channel_layer.group_send)(
            get_channel_group_name(new_member.username),
            {"type": "handle_group_add", **message},
        )

        # Send a response to the client to let them know that the add
        # was successful.
        self.send_event_to_client(EventName.GROUP_ADD, message)

    def handle_create_message(self, event):
        self.send_event_to_client(EventName.GROUP_MESSAGE, event)

    def handle_create_friend_request(self, event):
        self.send_event_to_client(EventName.USER_FRIEND_REQUEST, event)

    def handle_group_add(self, event):
        chat_group_id = event["chat_group"]
        async_to_sync(self.channel_layer.group_add)(
            f"chat_{chat_group_id}", self.channel_name
        )

        self.send_event_to_client(EventName.GROUP_ADD, event)

    def send_event_to_client(self, event_type: EventName, message):
        if "type" in message:
            del message["type"]

        self.send_json({"event_type": event_type.value, "message": message})

    def send_err_event_to_client(self, err_type: EventErrCode):
        self.send_event_to_client(EventName.ERROR_EVENT, err_type.value)
