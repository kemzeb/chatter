from django.urls import path

from chat.views import ChatGroupDetail, CreateChatGroup

urlpatterns = [
    path("chatgroups/", CreateChatGroup.as_view()),
    path("chatgroups/<int:pk>/", ChatGroupDetail.as_view()),
]
