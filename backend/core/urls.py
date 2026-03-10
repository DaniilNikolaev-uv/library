from django.contrib import admin
from django.urls import include, path

from swagger.swagger import schema_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("api/auth/", include("accounts.urls")),
    path("api/catalog/", include("catalog.urls")),
    path("api/inventory", include("inventory.urls")),
    path("api/circulation", include("circulation.urls")),
]
