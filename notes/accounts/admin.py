from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .forms_admin import UserCreationForm, UserChangeForm

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form = UserChangeForm   
    add_form = UserCreationForm

    readonly_fields = ("last_login", "date_joined")

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')

    fieldsets = (
        ("Datos de acceso", {'fields': ('email', 'password')}),
        ("Información personal", {'fields': ('first_name', 'last_name')}),
        ("Permisos", {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ("Fechas", {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "password1", "password2", "is_active", "is_staff", "is_superuser", "groups"),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)



# Register your models here.
