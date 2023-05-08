from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import FriendRequestViewSet, FriendsListView, RegisterView

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

user_me_urlpatterns = [
    path("friends/", FriendsListView.as_view()),
    *router.urls,
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("me/", include(user_me_urlpatterns)),
]
