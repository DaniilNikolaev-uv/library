from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, ReaderMeView, RegisterReaderView

urlpatterns = [
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),
    path("me/reader/", ReaderMeView.as_view()),
    path("register-reader/", RegisterReaderView.as_view()),
]
