from django.urls import path
from rest_framework.routers import DefaultRouter

from chat.views import ChatGroupMemberViewSet, ChatGroupViewSet, CreateChatMessage

urlpatterns = [
    path("messages/", CreateChatMessage.as_view()),
]

router = DefaultRouter()
router.register("", ChatGroupViewSet, basename="chats")
router.register(
    r"(?P<chat_id>\d+)/members", ChatGroupMemberViewSet, basename="chat_members"
)
urlpatterns += router.urls
