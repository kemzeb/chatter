from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet

from chatter.utils import publish_to_user
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


class FriendRequestViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request):
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

        addressee_has_sent_friend_request = FriendRequest.objects.filter(
            requester=addressee, addressee=user
        ).exists()
        if addressee_has_sent_friend_request:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_and_addressee_are_already_friends = user.friends.contains(addressee)
        if user_and_addressee_are_already_friends:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            friend_request = FriendRequest.objects.create(
                requester=user, addressee=addressee
            )
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = serializers.FriendRequestSerializer(friend_request)
            publish_to_user(addressee, serializer.data, "handle_create_friend_request")

            return Response(
                status=status.HTTP_201_CREATED, data={"id": friend_request.pk}
            )

    def destroy(self, request, pk=None):
        """Accepts a friend request. If it gets query parameter `?accept=1`, it will
        delete the friend request entry, make the auth user and requester friends, and
        publish a WebSocket event to the requester and auth user (the addressee).
        Otherwise if it equals '0', it will do everything mentioned above but won't make
        the 2 users friends.

        This event will contain both the addressee's and requester's user info (by
        using `ChatterUserSerializer`).
        """
        accept = request.query_params.get("accept")
        if accept not in ("0", "1"):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        friend_request = get_object_or_404(
            FriendRequest.objects.select_related("requester", "addressee"), pk=pk
        )
        user = request.user
        if friend_request.addressee != user:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        requester = friend_request.requester
        friend_request.delete()

        handler = "handle_accept_friend_request"
        if accept == "1":
            requester.friends.add(user)
        else:
            handler = "handle_reject_friend_request"

        serializer = serializers.DestroyFriendRequestSerializer(friend_request)
        publish_to_user(requester, serializer.data, handler)
        publish_to_user(user, serializer.data, handler)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        user = request.user
        serializer = serializers.ListFriendRequestSerializer(
            user.pending_requests.all(), many=True
        )

        return Response(serializer.data)
