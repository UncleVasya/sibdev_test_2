from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

app_name = 'users'


urlpatterns = [
    path(
        'register/',
        UserViewSet.as_view({'post': 'create'}),
        name='register'
    ),
    path(
        'login/',
        TokenObtainPairView.as_view(),
        name='login',
    ),
    path(
        'token-refresh/',
        TokenRefreshView.as_view(),
        name='token-refresh',
    )
]
