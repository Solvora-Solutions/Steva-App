from django.contrib import admin
from django.core.exceptions import ValidationError
from django import forms
from .models import Student
from Parent.models import Parent


class StudentForm(forms.ModelForm):
    """Custom form for Student model with validation."""

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'current_class', 'is_active']

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if not first_name or not first_name.strip():
            raise ValidationError("First name is required.")
        return first_name.strip().title()

    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if not last_name or not last_name.strip():
            raise ValidationError("Last name is required.")
        return last_name.strip().title()

    def clean_current_class(self):
        current_class = self.cleaned_data.get('current_class')
        if not current_class or not current_class.strip():
            raise ValidationError("Current class is required.")
        return current_class.strip().upper()


class ParentInline(admin.TabularInline):
    """Inline relation for linking parents to a student."""
    model = Student.parents.through
    extra = 1
    autocomplete_fields = ['parent']
    verbose_name = "Parent"
    verbose_name_plural = "Parents"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentForm
    list_display = (
        'student_id', 'first_name', 'last_name', 'current_class',
        'is_active', 'linked_parents_count', 'created_at'
    )
    list_filter = ('is_active', 'current_class', 'created_at')
    search_fields = (
        'student_id', 'first_name', 'last_name', 'current_class',
        'parents__user__first_name', 'parents__user__last_name'
    )
    readonly_fields = ('student_id', 'created_at', 'updated_at')
    inlines = [ParentInline]

    fieldsets = (
        ('Student Information', {
            'fields': ('student_id', 'first_name', 'last_name', 'current_class'),
        }),
        ('Additional Details', {
            'fields': ('is_active',),
            'classes': ('collapse',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def linked_parents_count(self, obj):
        """Display number of linked parents."""
        return obj.parents.count()
    linked_parents_count.short_description = "No. of Parents"

    def save_model(self, request, obj, form, change):
        """Auto-generate student_id if missing."""
        if not obj.student_id:
            last_student = Student.objects.order_by('-id').first()
            if last_student and last_student.student_id and last_student.student_id.startswith("SA"):
                try:
                    num = int(last_student.student_id.replace("SA", "")) + 1
                except ValueError:
                    num = Student.objects.count() + 1
            else:
                num = 1
            obj.student_id = f"SA{num:03d}"
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        """Optimize queries with prefetch_related for parents and users."""
        return super().get_queryset(request).prefetch_related('parents__user')

    def get_readonly_fields(self, request, obj=None):
        """Keep student_id readonly for existing objects."""
        readonly_fields = list(self.readonly_fields)
        if obj and 'student_id' not in readonly_fields:
            readonly_fields.append('student_id')
        return readonly_fields
