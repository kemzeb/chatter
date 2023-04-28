from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.serializers import CreateChatGroupSerializer


class CreateChatGroup(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CreateChatGroupSerializer(data=request.data)

        if serializer.is_valid():
            chat_group = serializer.save()
            chat_group.members.add(request.user)
            return Response(status=status.HTTP_201_CREATED, data={"id": chat_group.pk})

        return Response(status=status.HTTP_400_BAD_REQUEST)
