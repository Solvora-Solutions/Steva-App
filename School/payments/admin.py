from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reference', 'payer', 'student', 'fee_type', 'amount_display', 'status', 'verified', 'created_at')
    search_fields = ('reference', 'payer__email', 'student__student_id', 'student__first_name', 'student__last_name')
    list_filter = ('fee_type', 'status', 'verified', 'created_at')
    readonly_fields = ('reference', 'created_at', 'updated_at', 'metadata')


    def amount_display(self, obj):
        return obj.amount_display()
    amount_display.short_description = 'Amount'

    def student_info(self, obj):
        """Show student ID + full name in one column"""
        return f"{obj.student.student_id} - {obj.student.first_name} {obj.student.last_name}"
    student_info.short_description = "Student"
