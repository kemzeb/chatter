from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import FriendRequestView, FriendsListView, RegisterView

auth_urlpatterns = [
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "login/refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),
    path("register/", RegisterView.as_view(), name="register"),
]

user_me_urlpatterns = [
    path("friends/", FriendsListView.as_view()),
    path("friendrequests/", FriendRequestView.as_view()),
]

urlpatterns = [
    path("auth/", include(auth_urlpatterns)),
    path("me/", include(user_me_urlpatterns)),
]
