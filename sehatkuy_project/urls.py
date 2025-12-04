from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("users/", include("users.urls")),
    path("consultation/", include(("consultation.urls", "consultation"), namespace="consultation")),
    path("adminpanel/", include(("adminpanel.urls", "adminpanel"), namespace="adminpanel")),
    path("doctors/", include(("doctors.urls", "doctors"), namespace="doctors")),
    path("poliklinik/", include("poliklinik.urls")),
    path("appointments/", include(("appointments.urls", "appointments"), namespace="appointments")),
    path("pharmacy/", include("pharmacy.urls")),
    path("articles/", include(("articles.urls", "articles"), namespace="articles")),
    path("laboratorium/", include(("laboratory.urls", "laboratory"), namespace="laboratory")),
    path("emergency/", include(("emergency.urls", "emergency"), namespace="emergency")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
