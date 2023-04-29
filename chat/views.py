from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat import serializers
from chat.models import ChatGroup, ChatMessage
from chatter.utils import get_group_name


class CreateChatGroup(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.CreateChatGroupSerializer(data=request.data)

        if serializer.is_valid():
            chat_group = serializer.save()
            chat_group.members.add(request.user)
            return Response(status=status.HTTP_201_CREATED, data={"id": chat_group.pk})

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChatGroupDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=pk)

        # Make sure the user is a member of the group, else they can ust fetch the
        # details of any group!
        is_member = chat_group.members.contains(request.user)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.ChatGroupDetailSerializer(chat_group)

        return Response(serializer.data)


class CreateChatMessage(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.CreateMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data
        chat_group = get_object_or_404(
            ChatGroup.objects.all(), pk=data["from_chat_group"]
        )

        # Make sure the user is a member of the group, else they can send a message to
        # any chat group!
        is_member = chat_group.members.contains(request.user)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)

        message = ChatMessage.objects.create(
            from_user=request.user, from_chat_group=chat_group, message=data["message"]
        )

        new_message_serializer = serializers.ChatMessageSerializer(message)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            get_group_name(str(chat_group.pk)),
            {"type": "handle_create_message", **new_message_serializer.data},
        )

        return Response(status=status.HTTP_201_CREATED, data={"id": message.pk})
