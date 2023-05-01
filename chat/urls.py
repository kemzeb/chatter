from django.urls import path
from rest_framework.routers import DefaultRouter

from chat.views import ChatGroupMemberViewSet, ChatGroupViewSet, CreateChatMessage

urlpatterns = [
    path("messages/", CreateChatMessage.as_view()),
]

router = DefaultRouter()
router.register(r"chatgroups", ChatGroupViewSet)
router.register(r"chatgroups/(?P<chat_id>\d+)/members", ChatGroupMemberViewSet)
urlpatterns += router.urls
