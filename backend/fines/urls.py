from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FinePolicyViewSet, FineViewSet

router = DefaultRouter()
router.register(r"", FineViewSet, basename="fine")
router.register(r"policies", FinePolicyViewSet, basename="fine-policy")

urlpatterns = [
    path("", include(router.urls)),
]

