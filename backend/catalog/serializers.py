from rest_framework import serializers
from catalog.models import Author, Book, Category, Publisher


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
        queryset=Author.objects.all(), source="authors", write_only=True
    )
    categories = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), many=True, required=False
    )

    class Meta:
        model = Book
        fields = [
            "id", "title", "subtitle", "authors", "author_ids",
            "isbn", "year", "categories", "language", "description",
            "publisher", "cover_image"
        ]
        read_only_fields = ["id"]
