from rest_framework import serializers

from users.serializers import ChatterUserSerializer

from .models import ChatGroup, ChatMessage


class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["owner", "name"]


class ChatGroupListSerializer(serializers.ModelSerializer):
    """Serializes the output of `list()` in `chat.views.ChatGroupViewSet`."""

    owner = ChatterUserSerializer()

    class Meta:
        model = ChatGroup
        fields = ["owner", "name"]
        read_only_fields = [*fields]


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = "__all__"


class ChatGroupDetailSerializer(serializers.ModelSerializer):
    owner = ChatterUserSerializer(read_only=True)
    members = ChatterUserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()

    class Meta:
        model = ChatGroup
        fields = ["id", "owner", "members", "messages", "created"]

    def get_messages(self, obj):
        messages = obj.messages.all().order_by("created")
        return ChatMessageSerializer(messages, many=True).data


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["chat_group", "message"]


# FIXME: There must be a better way to implement serializers then this.
class ReadOnlyChatterUserSerializer(serializers.Serializer):
    """
    Exists only to validate input for `chat.views.ChatGroupMemberViewSet`'s `create()`.
    """

    id = serializers.IntegerField()
    username = serializers.CharField(max_length=1800, required=False)


class CreateChatGroupMemberSerializer(serializers.Serializer):
    chat_group = serializers.IntegerField()
    member = ReadOnlyChatterUserSerializer()
