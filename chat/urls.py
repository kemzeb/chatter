from django.urls import path

from chat.views import CreateChatGroup

urlpatterns = [
    path("chatgroups/", CreateChatGroup.as_view()),
]
