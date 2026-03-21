from rest_framework import serializers
from accounts.models import User, Reader


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role", "is_active", "is_staff"]
        read_only_fields = ["id"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "password", "role", "is_active", "is_staff"]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


class ReaderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="user", write_only=True
    )

    class Meta:
        model = Reader
        fields = [
            "id",
            "user",
            "user_id",
            "card_number",
            "phone_number",
            "email",
            "address",
            "date_registered",
            "is_blocked",
        ]
        read_only_fields = ["id", "date_registered"]
