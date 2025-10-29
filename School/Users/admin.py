from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    model = User

    # Columns to display in the admin list view
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_superuser')
    list_filter = ('role', 'is_superuser', 'is_active')

    # Fields to display when editing a user
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {'fields': ('role', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    # Fields to display when creating a new user in admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'role', 'password1', 'password2', 'is_active', 'is_superuser'),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Make sure the password form works for your custom user
    filter_horizontal = ('groups', 'user_permissions',)
