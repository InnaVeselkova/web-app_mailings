from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Путь к админ-панели
    path('users/', include('users.urls')),  # Путь к URLs приложения users
    path('mailings/', include('mailings.urls')),  # Путь к URLs приложения mailings
]
