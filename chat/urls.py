from rest_framework.routers import DefaultRouter

from chat.views import ChatGroupMemberViewSet, ChatGroupViewSet, ChatMessageViewSet

router = DefaultRouter()
router.register(
    r"(?P<chat_id>\d+)/members", ChatGroupMemberViewSet, basename="chat_member"
)
router.register(
    r"(?P<chat_id>\d+)/messages", ChatMessageViewSet, basename="chat_message"
)
router.register(r"", ChatGroupViewSet, basename="chat")

urlpatterns = router.urls
