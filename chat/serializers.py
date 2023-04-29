from rest_framework import serializers

from users.models import FriendRequest
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


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ["addressee"]


class ChatGroupAddUserSerializer(serializers.Serializer):
    chat_group = serializers.IntegerField(min_value=0)
    new_member = serializers.IntegerField(min_value=0)
