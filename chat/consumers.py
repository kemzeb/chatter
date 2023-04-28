from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.db import IntegrityError

from chat import serializers
from chat.models import ChatGroup, ChatMessage
from users.models import ChatterUser, FriendRequest

from .utils import EventErrCode, EventName


class ChatConsumer(JsonWebsocketConsumer):
    """
    The main consumer to handle events relating to:
    - Chat groups
    - Messaging

    It contains custom events that are sent between
    client, server, and channel layer. The following
    represent the custom event names:
    - group:message         Receive client messages and send to named group
    - user:friendrequest    Create a friend request record and send it to addressee
    """

    def connect(self):
        user = self.scope["user"]

        if not user.is_anonymous:
            chat_groups = ChatGroup.objects.filter(members__id=user.id)
            chat_group_list = []

            self.accept()

            async_to_sync(self.channel_layer.group_add)(
                f"user_{user.username}", self.channel_name
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
                    f"chat_{chat_group.pk}", self.channel_name
                )

            self.send_event_to_client(EventName.GROUP_CONNECT, chat_group_list)
        else:
            self.close()

    def disconnect(self, close_code):
        user = self.scope["user"]
        chat_groups = ChatGroup.objects.filter(members__id=user.id)

        async_to_sync(self.channel_layer.group_discard)(
            self._get_group_name_of_user(user), self.channel_name
        )

        for chat_group in chat_groups:
            async_to_sync(self.channel_layer.group_discard)(
                f"chat_{chat_group.pk}", self.channel_name
            )

    event_type = {
        str(EventName.GROUP_MESSAGE): "message_group_event",
        str(EventName.GROUP_ADD): "group_add_event",
        str(EventName.USER_FRIEND_REQUEST): "friend_request_event",
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

    def message_group_event(self, message):
        user = self.scope["user"]
        serializer = serializers.MessageChatGroupSerializer(data=message)

        if not serializer.is_valid():
            self.send_err_event_to_client(EventErrCode.SERIALIZATION)
            return

        data = serializer.data

        # Make sure the group exists.
        chat_group_manager = ChatGroup.objects.filter(id=data["from_chat_group"])

        if not chat_group_manager.exists():
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        chat_group = chat_group_manager[0]

        # Make sure the user is a member of the group.
        members_manager = chat_group.members.filter(id=user.id)

        if not members_manager.exists():
            self.send_err_event_to_client(EventErrCode.FORBIDDEN)
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
                "sent_on": str(new_message.sent_on),
            },
        )

    def friend_request_event(self, message):
        user = self.scope["user"]
        serializer = serializers.FriendRequestSerializer(data=message)
        if not serializer.is_valid():
            self.send_err_event_to_client(EventErrCode.SERIALIZATION)
            return

        addressee_id = serializer.data["addressee"]

        # Make sure the user is not trying to add themselves.
        if user.id == addressee_id:
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        user_manger = ChatterUser.objects.filter(id=addressee_id)
        if not user_manger.exists():
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        addressee = user_manger.first()

        # Make sure the addressee has not already sent a friend request.
        friend_request_manager = FriendRequest.objects.filter(
            requester=addressee, addressee=user
        )
        if friend_request_manager.exists():
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        # Make sure these users are not already friends.
        if user.friends.filter(id=addressee_id).exists():
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
            return

        try:
            friend_request = FriendRequest.objects.create(
                requester=user, addressee=addressee
            )
        except IntegrityError:
            self.send_err_event_to_client(EventErrCode.BAD_MESSAGE)
        else:
            # Send to addressee if they have an open channel.
            async_to_sync(self.channel_layer.group_send)(
                self._get_group_name_of_user(addressee),
                {
                    "type": "handle_friend_request",
                    "id": friend_request.pk,
                    "requester": user.id,
                },
            )
            self.handle_friend_request({"id": friend_request.pk, "requester": user.id})

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
            self._get_group_name_of_user(new_member),
            {"type": "handle_group_add", **message},
        )

        # Send a response to the client to let them know that the add
        # was successful.
        self.send_event_to_client(EventName.GROUP_ADD, message)

    def handle_chat_message(self, event):
        self.send_event_to_client(EventName.GROUP_MESSAGE, event)

    def handle_friend_request(self, event):
        self.send_event_to_client(EventName.USER_FRIEND_REQUEST, event)

    def handle_group_add(self, event):
        chat_group_id = event["chat_group"]
        async_to_sync(self.channel_layer.group_add)(
            f"chat_{chat_group_id}", self.channel_name
        )

        self.send_event_to_client(EventName.GROUP_ADD, event)

    def send_event_to_client(self, event_type: EventName, message):
        self.send_json({"event_type": event_type.value, "message": message})

    def send_err_event_to_client(self, err_type: EventErrCode):
        self.send_event_to_client(EventName.ERROR_EVENT, err_type.value)

    def _get_group_name_of_user(self, user) -> str:
        return f"user_{user.username}"
