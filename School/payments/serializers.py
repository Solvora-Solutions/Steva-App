from rest_framework import serializers
from .models import Payment
from django.contrib.auth import get_user_model
User = get_user_model()

class PaymentCreateSerializer(serializers.ModelSerializer):
    # Accept either amount (decimal/main units) or rely on fee_type lookup in view
    amount = serializers.DecimalField(max_digits=10,decimal_places=2,required=False,help_text="Amount in Ghana Cedis (e.g., 100.00 for GHS 100)")
    student_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Payment
        fields = ['fee_type', 'amount', 'student_id']

class PaymentDetailSerializer(serializers.ModelSerializer):
    payer_email = serializers.CharField(source='payer.email', read_only=True)
    student = serializers.SerializerMethodField()
    amount_display = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ['id', 'reference', 'payer_email', 'student', 'fee_type', 'amount', 'amount_display', 'status', 'verified', 'metadata', 'created_at']

    def get_student(self, obj):
        if obj.student:
            return {
                "student_id": obj.student.student_id,
                "first_name": obj.student.first_name,
                "last_name": obj.student.last_name,
            }
        return None

    def get_amount_display(self, obj):
        return obj.amount_display()
