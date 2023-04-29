from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from users import serializers
from users.models import ChatterUser
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
