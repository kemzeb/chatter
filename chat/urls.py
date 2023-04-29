from django.urls import path

from chat import views

urlpatterns = [
    path("chatgroups/", views.CreateChatGroup.as_view()),
    path("chatgroups/<int:pk>/", views.ChatGroupDetail.as_view()),
    path("messages/", views.CreateChatMessage.as_view()),
]
