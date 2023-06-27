from rest_framework import serializers

from users.serializers import ChatterUserSerializer

from .models import ChatGroup, ChatGroupMembership, ChatMessage


class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["owner", "name"]


class ChatGroupListSerializer(serializers.ModelSerializer):
    """Serializes the output of `list()` in `chat.views.ChatGroupViewSet`."""

    owner = ChatterUserSerializer()

    class Meta:
        model = ChatGroup
        fields = ["id", "owner", "name"]
        read_only_fields = [*fields]


class ChatGroupDetailSerializer(serializers.ModelSerializer):
    owner = ChatterUserSerializer(read_only=True)

    class Meta:
        model = ChatGroup
        fields = ["id", "owner", "created"]

    def get_messages(self, obj):
        messages = obj.messages.all().order_by("created")
        return ChatMessageSerializer(messages, many=True).data


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["id", "user", "chat_group", "message", "created"]


class CreateMessageSerializer(serializers.ModelSerializer):
    """
    Validates input for `create()` within `chat.views.ChatMessageViewSet`.
    """

    class Meta:
        model = ChatMessage
        fields = ["message"]


class PartialUpdateSerializer(serializers.ModelSerializer):
    """
    Validates input for `partial_update()` within `chat.views.ChatMessageViewSet`.
    """

    class Meta:
        model = ChatMessage
        fields = ["message"]


class ReadOnlyChatterUserSerializer(serializers.Serializer):
    """
    Validates input for `chat.views.ChatGroupMemberViewSet`.
    """

    id = serializers.IntegerField()
    username = serializers.CharField(max_length=1800, required=False)


class ChatGroupMemberSerializer(serializers.Serializer):
    chat_group = serializers.IntegerField()
    member = ReadOnlyChatterUserSerializer()


class ListChatGroupMemberSerializer(serializers.ModelSerializer):
    user = ReadOnlyChatterUserSerializer()

    class Meta:
        model = ChatGroupMembership
        fields = ["user", "chat_group", "joined"]
