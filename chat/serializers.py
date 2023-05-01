from rest_framework import serializers

from users.serializers import ChatterUserSerializer

from .models import ChatGroup, ChatMessage


class CreateChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["owner", "name"]


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
        fields = ["id", "owner", "members", "messages", "date_created"]

    def get_messages(self, obj):
        messages = obj.messages.all().order_by("sent_on")
        return ChatMessageSerializer(messages, many=True).data


class CreateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ["from_chat_group", "message"]


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
