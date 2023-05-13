from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer

from chatter.utils import EventName, get_channel_group_name, get_group_name


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

        self.accept()

        user_group_name = get_channel_group_name(user.username)
        self._group_add(user_group_name)

        for chat_group in user.chat_groups.all():
            group_name = get_group_name(chat_group.pk)
            self._group_add(group_name)

    def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_anonymous:
            return

        user_group_name = get_channel_group_name(user.username)
        self._group_discard(user_group_name)

        for chat_group in user.chat_groups.all():
            group_name = get_group_name(chat_group.pk)
            self._group_discard(group_name)

    def handle_destroy_chat_group(self, event):
        chat_group_id = event["id"]
        group_name = get_group_name(chat_group_id)
        async_to_sync(self.channel_layer.group_discard)(group_name, self.channel_name)
        self.send_event_to_client(EventName.GROUP_DESTROY, event)

    def handle_create_message(self, event):
        self.send_event_to_client(EventName.GROUP_MESSAGE, event)

    def handle_create_friend_request(self, event):
        self.send_event_to_client(EventName.USER_FRIEND_REQUEST, event)

    def handle_accept_friend_request(self, event):
        self.send_event_to_client(EventName.USER_ACCEPT_FRIEND_REQUEST, event)

    def handle_reject_friend_request(self, event):
        self.send_event_to_client(EventName.USER_REJECT_FRIEND_REQUEST, event)

    def handle_create_group_member(self, event):
        """Handles an event sent from `create()` in `ChatGroupMemberViewSet`."""
        chat_group_id = event["chat_group"]
        new_member_id = event["member"]["id"]
        user_id = self.scope["user"].id
        if new_member_id == user_id:
            group_name = get_group_name(chat_group_id)
            self._group_add(group_name)
        self.send_event_to_client(EventName.GROUP_ADD, event)

    def handle_destroy_group_member(self, event):
        """Handles an event sent from `destroy()` in `ChatGroupMemberViewSet`."""
        self.send_event_to_client(EventName.GROUP_REMOVE, event)

    def send_event_to_client(self, event_type: EventName, message):
        if "type" in message:
            del message["type"]

        self.send_json({"event_type": event_type.value, "message": message})

    def _group_add(self, group_name: str) -> None:
        async_to_sync(self.channel_layer.group_add)(group_name, self.channel_name)

    def _group_discard(self, group_name: str) -> None:
        async_to_sync(self.channel_layer.group_discard)(group_name, self.channel_name)
