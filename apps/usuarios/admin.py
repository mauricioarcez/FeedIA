from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'user_type', 'nombre_negocio')
    list_filter = ('user_type', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Información adicional', {
            'fields': ('user_type', 'puntos', 'nombre_negocio', 'provincia', 'ciudad', 'genero')
        }),
    )
