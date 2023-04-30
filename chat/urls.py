from django.urls import path
from rest_framework.routers import DefaultRouter

from chat.views import ChatGroupViewSet, CreateChatMessage

urlpatterns = [
    path("messages/", CreateChatMessage.as_view()),
]

router = DefaultRouter()
router.register(r"chatgroups", ChatGroupViewSet)
urlpatterns += router.urls
