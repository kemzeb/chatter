from rest_framework import serializers

from .models import ChatGroup


class CreateChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = ["name"]
