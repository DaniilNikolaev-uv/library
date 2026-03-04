from django.contrib.auth import get_user_model
from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Reader
from .serializers import (
    ReaderSerializer,
    RegisterReaderSerializer,
    RegisterSerializer,
    UserSerializer,
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterReaderView(generics.CreateAPIView):
    serializer_class = RegisterReaderSerializer
    permission_classes = [permissions.AllowAny]


class ReaderMeView(generics.RetrieveUpdateAPIView):
    serializer_class = ReaderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.reader_profile
