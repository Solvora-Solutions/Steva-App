from django.contrib import admin
from .models import Parent
from .forms import ParentForm


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    form = ParentForm
    list_display = ("full_name", "phone_number", "verified", "is_primary", "created_at")
    list_filter = ("verified", "is_primary", "created_at")
    search_fields = ("user__first_name", "user__last_name", "phone_number", "user__email")
    ordering = ("user__first_name", "user__last_name")

    fieldsets = (
        ("User Information", {
            "fields": ("first_name", "last_name", "email", "password1", "password2"),
        }),
        ("Parent Profile", {
            "fields": ("phone_number", "is_primary", "verified"),
        }),
    )
