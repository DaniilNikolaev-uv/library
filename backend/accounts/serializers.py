from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Reader, Staff

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role"]


class ReaderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reader
        fields = [
            "id",
            "user",
            "card_number",
            "phone_number",
            "email",
            "address",
            "date_registered",
            "is_blocked",
        ]


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = [
            "id",
            "user",
            "role",
        ]


class RegisterReaderSerializer(serializers.Serializer):
    """Регистрация читателя — создаёт User + Reader за один запрос."""

    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    password = serializers.CharField(write_only=True, min_length=8)
    card_number = serializers.CharField(max_length=50)
    phone = serializers.CharField(max_length=20, required=False, default="")
    address = serializers.CharField(required=False, default="")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email уже занят")
        return value

    def validate_card_number(self, value):
        if Reader.objects.filter(card_number=value).exists():
            raise serializers.ValidationError("Номер билета уже существует")
        return value

    def create(self, validated_data):
        card_number = validated_data.pop("card_number")
        phone = validated_data.pop("phone", "")
        address = validated_data.pop("address", "")

        user = User.objects.create_user(**validated_data, role=User.Role.READER)
        reader = Reader.objects.create(
            user=user, card_number=card_number, phone=phone, address=address
        )
        return reader
