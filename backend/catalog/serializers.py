from rest_framework import serializers
from catalog.models import Author, Book, Category, Publisher
from catalog.covers import PLACEHOLDER_COVER_URL, get_cover_url


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = [
            "id", "first_name", "last_name", "middle_name",
            "date_of_birth", "date_of_death", "description"
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "parent"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["id", "name", "country", "city"]


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    author_ids = serializers.PrimaryKeyRelatedField(
        queryset=Author.objects.all(), source="authors", write_only=True, many=True
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Book
        fields = [
            "id", "title", "subtitle", "authors", "author_ids",
            "isbn", "year", "categories", "language", "description",
            "publisher", "cover_image", "cover_url"
        ]
        read_only_fields = ["id"]

    def _resolve_cover_url(self, isbn: str | None, current_value: str | None = None) -> str:
        if isbn:
            return get_cover_url(isbn)
        if current_value:
            return current_value
        return PLACEHOLDER_COVER_URL

    def create(self, validated_data):
        isbn = validated_data.get("isbn")
        validated_data["cover_url"] = self._resolve_cover_url(isbn)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        isbn = validated_data.get("isbn", instance.isbn)
        validated_data["cover_url"] = self._resolve_cover_url(
            isbn,
            current_value=instance.cover_url,
        )
        return super().update(instance, validated_data)
