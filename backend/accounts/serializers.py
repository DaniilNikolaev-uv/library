from rest_framework import serializers
from accounts.models import User, Reader, Role, Staff


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
        if user.role in (Role.ADMIN, Role.LIBRARIAN):
            Staff.objects.get_or_create(user=user, defaults={"role": user.role})
        return user


class ReaderRegisterSerializer(serializers.Serializer):
    """
    Регистрация читателя по email и паролю.
    Создает User с ролью READER и связанный Reader-профиль.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value

    def create(self, validated_data):
        phone_number = validated_data.pop("phone_number", "")
        address = validated_data.pop("address", "")
        email = validated_data["email"]
        user = User.objects.create_user(
            email=email,
            password=validated_data["password"],
            first_name=validated_data.get("first_name", "").strip(),
            last_name=validated_data.get("last_name", "").strip(),
            role=Role.READER,
        )
        reader = Reader.objects.create(
            user=user,
            card_number=f"CARD-{user.id:06d}",
            phone_number=phone_number,
            email=email,
            address=address,
        )
        return reader


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
