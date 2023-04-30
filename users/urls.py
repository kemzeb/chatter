from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users import views

urlpatterns = [
    path(
        "auth/",
        include(
            [
                path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
                path(
                    "login/refresh/",
                    TokenRefreshView.as_view(),
                    name="token_refresh",
                ),
                path("register/", views.RegisterView.as_view(), name="register"),
            ]
        ),
    ),
    path("friends/", views.FriendsListView.as_view()),
    path("friendrequests/", views.FriendRequestView.as_view()),
]
