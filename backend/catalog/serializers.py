from rest_framework import serializers
from catalog.models import Author, Book, Category, Publisher
from catalog.covers import PLACEHOLDER_COVER_URL, get_cover_url, lookup_isbn


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
    cover_image = serializers.SerializerMethodField()
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

    def get_cover_image(self, obj):
        try:
            if not obj.cover_image:
                return None
            return obj.cover_image.url
        except Exception:
            # Do not break catalog listing when external storage is unavailable.
            return None

    def _resolve_cover_url(self, isbn: str | None, current_value: str | None = None) -> str:
        if isbn:
            return get_cover_url(isbn)
        if current_value:
            return current_value
        return PLACEHOLDER_COVER_URL

    def _resolve_isbn(self, validated_data, instance=None) -> str | None:
        explicit_isbn = validated_data.get("isbn")
        if explicit_isbn:
            return explicit_isbn
        if instance and instance.isbn:
            return instance.isbn

        title = validated_data.get("title") or getattr(instance, "title", "") or ""
        authors = validated_data.get("authors")
        author_name = None
        if authors:
            first_author = authors[0]
            author_name = " ".join(
                x for x in [first_author.first_name, first_author.last_name] if x
            ).strip()
        elif instance:
            first_author = instance.authors.first()
            if first_author:
                author_name = " ".join(
                    x for x in [first_author.first_name, first_author.last_name] if x
                ).strip()
        return lookup_isbn(title=title, author=author_name)

    def create(self, validated_data):
        isbn = self._resolve_isbn(validated_data)
        validated_data["isbn"] = isbn
        validated_data["cover_url"] = self._resolve_cover_url(isbn)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        isbn = self._resolve_isbn(validated_data, instance=instance)
        validated_data["isbn"] = isbn
        validated_data["cover_url"] = self._resolve_cover_url(
            isbn,
            current_value=instance.cover_url,
        )
        return super().update(instance, validated_data)
