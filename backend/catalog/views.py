from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from .models import Author, Book, Category, Publisher
from .serializers import (
    AuthorSerializer,
    BookDetailSerializer,
    BookSerializer,
    CategorySerializer,
    PublisherSerializer,
)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["first_name", "last_name"]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related("publisher").prefetch_related(
        "authors", "categories"
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["year", "language", "categories", "authors"]
    search_fields = ["title", "subtitle", "isbn", "authors__last_name"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer
