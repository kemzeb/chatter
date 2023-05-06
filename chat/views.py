from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from chat import serializers
from chat.models import ChatGroup, ChatMessage
from chatter.utils import get_channel_group_name, get_group_name
from users.models import ChatterUser


class ChatGroupViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
        serializer = serializers.ChatGroupSerializer(data=request.data)
        if serializer.is_valid():
            chat_group = serializer.save()
            chat_group.members.add(request.user)
            return Response(status=status.HTTP_201_CREATED, data={"id": chat_group.pk})

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=pk)

        # Make sure the user is a member of the group, else they can ust fetch the
        # details of any group!
        is_member = chat_group.members.contains(request.user)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = serializers.ChatGroupDetailSerializer(chat_group)
        return Response(serializer.data)

    def list(self, request):
        user = request.user
        queryset = user.chat_groups.all()
        serializer = serializers.ChatGroupListSerializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=pk)
        user = request.user

        if user != chat_group.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        chat_group.delete()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            get_group_name(pk),
            {"type": "handle_destroy_chat_group", "id": pk},
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatGroupMemberViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, chat_id=None):
        serializer = serializers.ReadOnlyChatterUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not chat_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=chat_id)

        new_member_id = serializer.data["id"]
        new_member = get_object_or_404(ChatterUser.objects.all(), id=new_member_id)
        user = request.user
        has_friendship_with_user = new_member.friends.contains(user)
        if not has_friendship_with_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        is_already_a_member = chat_group.members.contains(new_member)
        if is_already_a_member:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if chat_group.owner != user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        chat_group.members.add(new_member)

        new_member_data = {
            "chat_group": chat_group.pk,
            "member": {"id": new_member.pk, "username": new_member.username},
        }
        new_member_serializer = serializers.ChatGroupMemberSerializer(
            data=new_member_data
        )
        if not new_member_serializer.is_valid():
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            get_channel_group_name(new_member.username),
            {"type": "handle_create_group_member", **new_member_serializer.data},
        )
        async_to_sync(channel_layer.group_send)(
            get_group_name(chat_group.pk),
            {"type": "handle_create_group_member", **new_member_serializer.data},
        )

        return Response(status=status.HTTP_201_CREATED, data=new_member_serializer.data)

    def destroy(self, request, chat_id=None, pk=None):
        if chat_id is None or pk is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=chat_id)
        user = request.user
        if user != chat_group.owner:
            return Response(status=status.HTTP_403_FORBIDDEN)

        member = get_object_or_404(ChatterUser.objects.all(), id=pk)
        if not chat_group.members.contains(member):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        chat_group.members.remove(member)

        new_member_data = {
            "chat_group": chat_group.pk,
            "member": {"id": member.pk, "username": member.username},
        }
        new_member_serializer = serializers.ChatGroupMemberSerializer(
            data=new_member_data
        )
        if not new_member_serializer.is_valid():
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            get_group_name(chat_group.pk),
            {"type": "handle_destroy_group_member", **new_member_serializer.data},
        )

        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateChatMessage(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.CreateMessageSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = serializer.data
        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=data["chat_group"])

        # Make sure the user is a member of the group, else they can send a message to
        # any chat group!
        is_member = chat_group.members.contains(request.user)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)

        message = ChatMessage.objects.create(
            user=request.user, chat_group=chat_group, message=data["message"]
        )

        new_message_serializer = serializers.ChatMessageSerializer(message)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            get_group_name(chat_group.pk),
            {"type": "handle_create_message", **new_message_serializer.data},
        )

        return Response(status=status.HTTP_201_CREATED, data={"id": message.pk})
