from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import ChatGroup
from chat.serializers import ChatGroupDetailSerializer, CreateChatGroupSerializer


class CreateChatGroup(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateChatGroupSerializer(data=request.data)

        if serializer.is_valid():
            chat_group = serializer.save()
            chat_group.members.add(request.user)
            return Response(status=status.HTTP_201_CREATED, data={"id": chat_group.pk})

        return Response(status=status.HTTP_400_BAD_REQUEST)


class ChatGroupDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatGroupDetailSerializer

    def get(self, request, pk=None):
        chat_group = get_object_or_404(ChatGroup.objects.all(), pk=pk)

        # Make sure the user is a member of the group, else an authenticated user can
        # just fetch the details of any group!
        is_member = chat_group.members.contains(request.user)
        if not is_member:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = ChatGroupDetailSerializer(chat_group)

        return Response(serializer.data)
