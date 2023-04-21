from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import FriendsListView, RegisterView

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
                path("register/", RegisterView.as_view(), name="register"),
            ]
        ),
    ),
    path("<int:pk>/friends/", FriendsListView.as_view()),
]
