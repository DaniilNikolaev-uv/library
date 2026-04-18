import json
from urllib.parse import urlencode
from urllib.request import urlopen

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from catalog.covers import PLACEHOLDER_COVER_URL, get_cover_url
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
