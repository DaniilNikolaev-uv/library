from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import MeView, ReaderMeView, RegisterReaderView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view()),  # просто User
    path("register-reader/", RegisterReaderView.as_view()),  # User + Reader
    path("login/", TokenObtainPairView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/", MeView.as_view()),
    path("me/reader/", ReaderMeView.as_view()),
]
