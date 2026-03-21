from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from swagger.swagger import schema_view
from accounts.views import UserViewSet, ReaderViewSet
from catalog.views import AuthorViewSet, BookViewSet, CategoryViewSet, PublisherViewSet
from inventory.views import LocationViewSet, BookCopyViewSet
from circulation.views import LoanViewSet
from reservations.views import ReservationViewSet

router = DefaultRouter()
router.register(r"admin/users", UserViewSet)
router.register(r"admin/readers", ReaderViewSet)
router.register(r"admin/authors", AuthorViewSet)
router.register(r"admin/books", BookViewSet)
router.register(r"admin/categories", CategoryViewSet)
router.register(r"admin/publishers", PublisherViewSet)
router.register(r"admin/locations", LocationViewSet)
router.register(r"admin/book-copies", BookCopyViewSet)
router.register(r"admin/loans", LoanViewSet)
router.register(r"admin/reservations", ReservationViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/", include(router.urls)),
    path("api/auth/", include("accounts.urls")),
    path("api/catalog/", include("catalog.urls")),
    path("api/inventory/", include("inventory.urls")),
    path("api/circulation/", include("circulation.urls")),
    path("api/reservations/", include("reservations.urls")),
    path("api/fines/", include("fines.urls")),
    path("api/reports/", include("reports.urls")),
    path("api/audit/", include("audit.urls")),
]
