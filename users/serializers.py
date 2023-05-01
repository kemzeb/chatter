from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import ModelSerializer, Serializer

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


class CreateFriendRequestSerializer(ModelSerializer):
    """Exists only to validate input for `users.views.CreateFriendRequestView`."""

    class Meta:
        model = models.FriendRequest
        fields = ["addressee"]


class FriendRequestSerializer(ModelSerializer):
    class Meta:
        model = models.FriendRequest
        fields = "__all__"
