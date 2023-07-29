from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from chatter.utils import LOOKUP_REGEX, publish_to_user
from users import serializers
from users.models import ChatterUser, FriendRequest
from users.paginations import FriendSearchPagination


class RegisterView(CreateAPIView):
    model = ChatterUser
    permission_classes = [permissions.AllowAny]
    serializer_class = serializers.RegisterSerializer


class FriendSearchView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.ChatterUserSerializer
    pagination_class = FriendSearchPagination

    def get_queryset(self):
        q = self.request.query_params.get("q")
        if q is None:
            raise ValidationError(detail="Invalid query string given")
        user = self.request.user
        queryset = user.friends.filter(username__icontains=q)
        return queryset


class FriendsViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_value_regex = LOOKUP_REGEX

    def destroy(self, request, pk=None):
        friend = get_object_or_404(ChatterUser, pk=pk)
        user = request.user

        if not user.friends.contains(friend):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user.friends.remove(friend)

        user_serializer = serializers.ChatterUserSerializer(user)
        friend_serializer = serializers.ChatterUserSerializer(friend)
        publish_to_user(user, friend_serializer.data, "handle_delete_friend")
        publish_to_user(friend, user_serializer.data, "handle_delete_friend")

        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        user = request.user
        serializer = serializers.ChatterUserSerializer(
            user.friends.order_by("username"), many=True
        )
        return Response(serializer.data)


class FriendRequestViewSet(ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    lookup_value_regex = LOOKUP_REGEX

    def create(self, request):
        serializer = serializers.CreateFriendRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pending_username = serializer.data["username"]
        user = request.user
        if user.username == pending_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user_manager = ChatterUser.objects.filter(username=pending_username)
        if not user_manager.exists():
            return Response(status=status.HTTP_404_NOT_FOUND)

        addressee = user_manager[0]
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
        serializer = serializers.DestroyFriendRequestSerializer(friend_request)
        data = serializer.data
        friend_request.delete()

        handler = "handle_accept_friend_request"
        if accept == "1":
            requester.friends.add(user)
        else:
            handler = "handle_reject_friend_request"

        publish_to_user(requester, data, handler)
        publish_to_user(user, data, handler)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request):
        user = request.user
        serializer = serializers.ListFriendRequestSerializer(
            user.pending_requests.all(), many=True
        )

        return Response(serializer.data)
