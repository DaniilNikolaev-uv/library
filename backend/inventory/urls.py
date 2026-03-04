from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookCopyViewSet, LocationViewSet

router = DefaultRouter()
router.register(r"copies", BookCopyViewSet, basename="bookcopy")
router.register(r"locations", LocationViewSet, basename="location")

urlpatterns = [
    path("", include(router.urls)),
]
