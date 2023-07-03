from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import (
    FriendRequestViewSet,
    FriendSearchView,
    FriendsViewSet,
    RegisterView,
)

auth_urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "login/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("register/", RegisterView.as_view(), name="register"),
]

router = DefaultRouter()
router.register(r"friendrequests", FriendRequestViewSet, basename="friend_requests")
router.register(r"friends", FriendsViewSet, basename="friends")

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path(
        "me/",
        include(router.urls + [path("friends/search/", FriendSearchView.as_view())]),
    ),
]
