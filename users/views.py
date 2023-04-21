from rest_framework import permissions
from rest_framework.generics import CreateAPIView, ListAPIView

from users.models import ChatterUser

from .serializers import ChatterUserSerializer, RegisterSerializer


class RegisterView(CreateAPIView):
    model = ChatterUser
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class FriendsListView(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ChatterUserSerializer

    def get_queryset(self):
        return ChatterUser.objects.exclude(id=self.request.user.pk)
