from rest_framework import viewsets, status, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from accounts.models import Reader, Staff
from accounts.serializers import (
    UserSerializer,
    UserCreateSerializer,
    ReaderSerializer,
    ReaderRegisterSerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-id")
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserSerializer


class ReaderViewSet(viewsets.ModelViewSet):
    queryset = Reader.objects.all().order_by("-id")
    serializer_class = ReaderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class ReaderMeView(generics.RetrieveUpdateAPIView):
    serializer_class = ReaderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.reader


class RegisterReaderView(generics.CreateAPIView):
    """
    Публичная регистрация читателя.

    POST /api/auth/register-reader/
    """

    serializer_class = ReaderRegisterSerializer
    permission_classes = [permissions.AllowAny]
