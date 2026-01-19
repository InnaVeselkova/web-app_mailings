from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import CustomUser

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    # Настраиваем отображение полей в админке
    fieldsets = (
        (None, {'fields': ('email', 'is_blocked',)}),
        ('Personal info', {'fields': ('phone_number', 'avatar', 'country')}),  # Удалено 'is_blocked' здесь
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_blocked',),
        }),
    )
    list_display = ('email', 'is_staff', 'is_blocked',)
    search_fields = ('email',)
    ordering = ('email',)

# Регистрируем кастомную модель пользователя в админке
admin.site.register(CustomUser, CustomUserAdmin)