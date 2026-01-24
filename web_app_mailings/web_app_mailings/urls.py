from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),  # Путь к админ-панели
    path("users/", include("users.urls")),  # Путь к URLs приложения users
    path("mailings/", include("mailings.urls")),
]

if settings.DEBUG:  # Только для отладки
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
