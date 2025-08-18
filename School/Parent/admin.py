from django.contrib import admin
from .models import Parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("full_name", "phone_number", "verified", "is_primary", "created_at")
    list_filter = ("verified", "is_primary", "created_at")
    search_fields = ("user__first_name", "user__last_name", "phone_number", "user__email")
    ordering = ("user__first_name", "user__last_name")

    fieldsets = (
        ("Parent Profile", {
            "fields": ("user", "phone_number", "is_primary", "verified"),
        }),
    )
