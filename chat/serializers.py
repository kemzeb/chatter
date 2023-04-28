from rest_framework import serializers

from users.models import FriendRequest

from .models import ChatGroup, ChatMessage


class CreateChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["owner", "name"]


class FetchChatGroupSerializer(serializers.Serializer):
    chat_group_id = serializers.IntegerField(min_value=0)


class MessageChatGroupSerializer(serializers.ModelSerializer):
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
