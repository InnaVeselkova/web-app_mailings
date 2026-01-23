from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser
from mailings.models import Mailing


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "is_blocked",
                )
            },
        ),
        ("Personal info", {"fields": ("phone_number", "avatar", "country")}),  # Удалено 'is_blocked' здесь
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_blocked",
                ),
            },
        ),
    )
    list_display = (
        "email",
        "is_staff",
        "is_blocked",
    )
    search_fields = ("email",)
    ordering = ("email",)


# Регистрируем кастомную модель пользователя в админке
admin.site.register(CustomUser, CustomUserAdmin)


class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "start_time", "end_time", "status", "owner")  # поля для отображения в списке
    list_filter = ("status",)  # фильтр по статусу
    search_fields = ("owner__username", "owner__email", "id")  # поиск по владельцу и id
    ordering = ("-start_time",)

    def has_change_permission(self, request, obj=None):
        # Запретить изменение
        return False

    def has_delete_permission(self, request, obj=None):
        # Разрешить удаление
        return True


# Регистрируем модель рассылки в админке
admin.site.register(Mailing, MailingAdmin)
