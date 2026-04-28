import json
from urllib.parse import urlencode
from urllib.request import urlopen

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Count, Q

from catalog.covers import PLACEHOLDER_COVER_URL, get_cover_url
from catalog.models import Author, Book, Category, Publisher
from catalog.serializers import AuthorSerializer, BookSerializer, CategorySerializer, PublisherSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework import filters


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all().order_by("last_name", "first_name")
    serializer_class = AuthorSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]


class PublisherViewSet(viewsets.ModelViewSet):
    queryset = Publisher.objects.all().order_by("name")
    serializer_class = PublisherSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by("-id")
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "subtitle", "isbn", "authors__last_name", "authors__first_name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAdminUser()]

    def get_queryset(self):
        """
        Публичный каталог с возможностью фильтрации:
        - ?category=<id>
        - ?year=<год>
        - ?available_only=true — только книги с доступными экземплярами.
        """
        qs = super().get_queryset().prefetch_related("authors", "categories")
        category_id = self.request.query_params.get("category")
        year = self.request.query_params.get("year")
        available_only = self.request.query_params.get("available_only")

        if category_id:
            qs = qs.filter(categories__id=category_id)
        if year:
            try:
                qs = qs.filter(year=int(year))
            except ValueError:
                pass
        if available_only and available_only.lower() in ("1", "true", "yes"):
            qs = qs.annotate(
                available_copies_count=Count(
                    "copies",
                    filter=Q(copies__status="available"),
                )
            ).filter(available_copies_count__gt=0)

        return qs


class ExternalBookSearchView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        query = (request.query_params.get("q") or "").strip()
        if not query:
            return Response({"detail": "Query parameter 'q' is required."}, status=status.HTTP_400_BAD_REQUEST)

        params = urlencode({"q": query, "limit": 10})
        url = f"https://openlibrary.org/search.json?{params}"
        try:
            with urlopen(url, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except Exception:
            return Response({"detail": "External provider is unavailable."}, status=status.HTTP_502_BAD_GATEWAY)

        results = []
        for doc in payload.get("docs", []):
            isbn_list = doc.get("isbn") or []
            isbn = isbn_list[0] if isbn_list else None
            authors = doc.get("author_name") or []
            results.append(
                {
                    "title": doc.get("title") or "",
                    "author": ", ".join(authors) if authors else "",
                    "isbn": isbn,
                    "cover_url": get_cover_url(isbn) if isbn else PLACEHOLDER_COVER_URL,
                }
            )

        return Response(results, status=status.HTTP_200_OK)
