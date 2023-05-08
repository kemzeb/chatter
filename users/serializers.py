from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer

from users import models


# https://stackoverflow.com/questions/16857450/how-to-register-users-in-django-rest-framework
class RegisterSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "username",
            "email",
            "password",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = get_user_model()(**validated_data)

        user.set_password(validated_data["password"])
        user.save()

        return user


class ChatterUserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]


class FriendRequestSerializer(ModelSerializer):
    """
    Exists only for serializing `FriendRequest` objects.
    """

    requester = ChatterUserSerializer()
    addressee = ChatterUserSerializer()

    class Meta:
        model = models.FriendRequest
        fields = ["id", "requester", "addressee"]
        read_only_fields = [*fields]


class CreateFriendRequestSerializer(ModelSerializer):
    """
    Exists only for validating user input for `create()` in
    `users.views.FriendRequestViewSet`.
    """

    class Meta:
        model = models.FriendRequest
        fields = ["addressee"]


class ListFriendRequestSerializer(ModelSerializer):
    """
    Exists only for `FriendRequest` serialization in `list()` within
    `users.views.FriendRequestViewSet`.
    """

    requester = ChatterUserSerializer()

    class Meta:
        model = models.FriendRequest
        fields = ["id", "requester"]
