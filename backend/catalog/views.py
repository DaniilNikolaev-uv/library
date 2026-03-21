from rest_framework import viewsets
from catalog.models import Author, Book, Category, Publisher
from catalog.serializers import AuthorSerializer, BookSerializer, CategorySerializer, PublisherSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by("last_name", "first_name")
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all().order_by("name")
    serializer_class = PublisherSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("-id")
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
