from django.contrib import admin
from .models import Student
from Parent.models import Parent

class ParentInline(admin.TabularInline):
    model = Student.parents.through
    extra = 1
    verbose_name = "Parent"
    verbose_name_plural = "Parents"

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'first_name', 'last_name', 'current_class', 'is_active', 'linked_parents')
    search_fields = ('student_id', 'first_name', 'last_name', 'current_class')
    list_filter = ('is_active', 'current_class')
    inlines = [ParentInline]
    readonly_fields = ('student_id',)  # 🔹 Make student_id read-only

    def linked_parents(self, obj):
        return ", ".join([f"{p.user.first_name} {p.user.last_name}" for p in obj.parents.all()])

    def save_model(self, request, obj, form, change):
        # Ensure student_id is generated if missing
        if not obj.student_id:
            last_student = Student.objects.order_by('-id').first()
            if last_student and last_student.student_id:
                num = int(last_student.student_id.replace("SA", "")) + 1
            else:
                num = 1
            obj.student_id = f"SA{num:03d}"
        super().save_model(request, obj, form, change)
