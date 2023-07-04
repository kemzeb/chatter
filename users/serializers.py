from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from users import models


# https://stackoverflow.com/questions/16857450/how-to-register-users-in-django-rest-framework
class RegisterSerializer(serializers.ModelSerializer):
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


class ChatterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username"]


class FriendRequestSerializer(serializers.ModelSerializer):
    """
    Exists only for serializing `FriendRequest` objects.
    """

    requester = ChatterUserSerializer()
    addressee = ChatterUserSerializer()

    class Meta:
        model = models.FriendRequest
        fields = ["id", "requester", "addressee"]
        read_only_fields = [*fields]


class CreateFriendRequestSerializer(serializers.Serializer):
    """
    Validates user input for `create()` within `users.views.FriendRequestViewSet`.
    """

    # https://docs.djangoproject.com/en/4.2/ref/contrib/auth/#django.contrib.auth.models.User.username
    username = serializers.CharField(max_length=150)


class DestroyFriendRequestSerializer(serializers.ModelSerializer):
    """
    Used for serialization for `destroy()` within `users.views.FriendRequestViewSet`.
    """

    requester = ChatterUserSerializer()
    addressee = ChatterUserSerializer()

    class Meta:
        model = models.FriendRequest
        fields = ["requester", "addressee"]
        read_only_fields = ["requester", "addressee"]
        write_only_fields = ["id"]


class ListFriendRequestSerializer(serializers.ModelSerializer):
    """
    Exists only for `FriendRequest` serialization in `list()` within
    `users.views.FriendRequestViewSet`.
    """

    requester = ChatterUserSerializer()

    class Meta:
        model = models.FriendRequest
        fields = ["id", "requester"]
