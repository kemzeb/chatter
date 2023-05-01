from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chat.models import ChatGroup
from chatter.utils import get_channel_group_name, get_group_name

from .utils import EventErrCode, EventName


class ChatConsumer(JsonWebsocketConsumer):
    """
    The main consumer that utilizes the Publisher-Subscriber pattern. It publishes user,
    chat group, and message-related events for any subscribing client to consume. Any
    messages sent by the client once a connection is established are ignored.
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
            async_to_sync(self.channel_layer.group_discard)(
                get_group_name(chat_group.pk), self.channel_name
            )

    def handle_create_message(self, event):
        self.send_event_to_client(EventName.GROUP_MESSAGE, event)

    def handle_create_friend_request(self, event):
        self.send_event_to_client(EventName.USER_FRIEND_REQUEST, event)

    def handle_create_group_member(self, event):
        """Handles an event sent from `create()` in `ChatGroupMemberViewSet`."""
        chat_group_id = event["chat_group"]
        new_member_id = event["member"]["id"]
        user_id = self.scope["user"].id
        if new_member_id == user_id:
            async_to_sync(self.channel_layer.group_add)(
                get_group_name(chat_group_id), self.channel_name
            )
        self.send_event_to_client(EventName.GROUP_ADD, event)

    def send_event_to_client(self, event_type: EventName, message):
        if "type" in message:
            del message["type"]

        self.send_json({"event_type": event_type.value, "message": message})

    def send_err_event_to_client(self, err_type: EventErrCode):
        self.send_event_to_client(EventName.ERROR_EVENT, err_type.value)
