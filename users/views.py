from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import IntegrityError
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from chatter.utils import get_channel_group_name
from users import serializers
from users.models import ChatterUser, FriendRequest
from users.paginations import UserSearchPagination


class RegisterView(CreateAPIView):
    model = ChatterUser
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.RegisterSerializer


class FriendsListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = serializers.ChatterUserSerializer(user.friends.all(), many=True)

        return Response(serializer.data)


class UserSearchView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatterUserSerializer
    pagination_class = UserSearchPagination

    def get_queryset(self):
        queryset = ChatterUser.objects.all()
        q = self.request.query_params.get("q")
        queryset = queryset.filter(username__contains=q).exclude(
            id=self.request.user.pk
        )
        return queryset


class FriendRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = serializers.CreateFriendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        addressee_id = serializer.data["addressee"]
        user = request.user

        if user.id == addressee_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_manger = ChatterUser.objects.filter(id=addressee_id)
        if not user_manger.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        addressee = user_manger[0]

        has_addressee_sent_friend_request = FriendRequest.objects.filter(
            requester=addressee, addressee=user
        ).exists()
        if has_addressee_sent_friend_request:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        is_user_and_addressee_already_friends = user.friends.contains(addressee)
        if is_user_and_addressee_already_friends:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.create(
                requester=user, addressee=addressee
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = serializers.FriendRequestSerializer(friend_request)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                get_channel_group_name(addressee),
                {"type": "handle_create_friend_request", **serializer.data},
            )

            return Response(
                status=status.HTTP_201_CREATED, data={"id": friend_request.pk}
            )
