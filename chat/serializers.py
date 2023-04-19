from rest_framework import serializers

from .models import ChatGroup


class CreateChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["name"]


class FetchChatGroupSerializer(serializers.Serializer):
    chat_group_id = serializers.IntegerField(min_value=0)
