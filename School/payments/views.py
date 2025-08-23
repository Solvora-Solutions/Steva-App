import uuid
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentCreateSerializer, PaymentDetailSerializer
from .paystack import Paystack
from Student.models import Student
from django.contrib.auth import get_user_model

from .at_client import sms

User = get_user_model()

# -------------------------------------------
# Fee structure (amounts in GHS, not pesewas)
# -------------------------------------------
FEE_AMOUNTS = {
    "tuition": 500.00,    # GHS 500.00
    "bus_fee": 100.00,    # GHS 100.00
    "feeding_fee": 20.00, # GHS 20.00
}

# -------------------------------------------
# Helper: Send SMS + Email Notifications
# -------------------------------------------
def send_payment_notifications(payment: Payment) -> None:
    parent_profile = getattr(payment.payer, "parent_profile", None)
    phone_number = getattr(parent_profile, "phone_number", None)
    email = payment.payer.email

    full_name = f"{payment.payer.first_name} {payment.payer.last_name}".strip()
    student_name = str(payment.student) if payment.student else "—"
    fee_display = (payment.fee_type or "").replace("_", " ").title()

    # SMS
    if phone_number:
        sms_message = (
            f"Hello {full_name}, your {fee_display} payment of GHS {payment.amount:.2f} "
            f"for {student_name} was successful. Ref: {payment.reference}. — Steva Academy"
        )
        try:
            sms.send(sms_message, [phone_number])
        except Exception as e:
            print(f"[SMS ERROR] {e}")

    # Email
    subject = "Payment Receipt — Steva Academy"
    body = (
        f"Dear {full_name},\n\n"
        f"We have successfully received your payment.\n\n"
        f"Amount:   GHS {payment.amount:.2f}\n"
        f"Type:     {fee_display}\n"
        f"Student:  {student_name}\n"
        f"Reference:{payment.reference}\n"
        f"Status:   {payment.status}\n\n"
        f"Thank you for your support.\n\n"
        f"Steva Academy Finance Office"
    )
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")


# -------------------------------------------
# Initialize a Paystack payment
# -------------------------------------------
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def initialize_payment(request):
    serializer = PaymentCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    fee_type = data.get("fee_type")
    amount_input = data.get("amount")       # in GHS
    student_id = data.get("student_id")

    #  Require student
    if not student_id:
        return Response({"error": "Student ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Get the student object
    student = get_object_or_404(Student, student_id=student_id)

    # Decide final amount in GHS
    if amount_input is not None:
        amount_ghs = float(amount_input)
    else:
        if fee_type not in FEE_AMOUNTS:
            return Response({"error": "Amount required for this fee type."}, status=status.HTTP_400_BAD_REQUEST)
        amount_ghs = FEE_AMOUNTS[fee_type]

    # Paystack

    # Paystack expects amount in pesewas
    amount_pesewas = int(amount_ghs * 100)

    reference = str(uuid.uuid4())
    paystack = Paystack()
    callback_url = request.build_absolute_uri(f"/api/v1/payments/verify/{reference}/")

    try:
        res = paystack.initialize_transaction(
            email=request.user.email,
            amount_pesewas=amount_pesewas,
            callback_url=callback_url,
            reference=reference,
        )
    except Exception as e:
        return Response(
            {"error": "Failed to initialize transaction", "details": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    if res.get("status") and res.get("data"):
        pay_ref = res["data"].get("reference") or reference
        Payment.objects.create(
            payer=request.user,
            student=student,
            fee_type=fee_type,
            amount=amount_ghs,   # ✅ Save in GHS
            reference=pay_ref,
            status="pending",
            metadata=res,
        )
        return Response(
            {
                "authorization_url": res["data"].get("authorization_url"),
                "reference": pay_ref,
                "message": "Initialized. Redirect user to authorization_url to complete payment.",
            },
            status=status.HTTP_201_CREATED,
        )

    return Response({"error": "Paystack initialization failed", "details": res}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------
# Verify payment
# -------------------------------------------
@api_view(["GET"])
@permission_classes([permissions.AllowAny])
def verify_payment(request, reference):
    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)

    paystack = Paystack()
    try:
        res = paystack.verify_transaction(reference)
    except Exception as e:
        return Response({"error": "Failed to verify transaction", "details": str(e)}, status=status.HTTP_502_BAD_GATEWAY)

    data_status = res.get("data", {}).get("status")
    if res.get("status") and data_status == "success":
        payment.verified = True
        payment.status = "success"
        payment.metadata = res
        payment.save()

        send_payment_notifications(payment)

        serializer = PaymentDetailSerializer(payment)
        return Response({"message": "Payment verified", "payment": serializer.data})

    payment.status = "failed"
    payment.metadata = res
    payment.save()
    return Response({"message": "Payment not successful", "details": res}, status=status.HTTP_400_BAD_REQUEST)


# -------------------------------------------
# List my payments
# -------------------------------------------
@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def list_my_payments(request):
    qs = Payment.objects.filter(payer=request.user).order_by("-created_at")
    serializer = PaymentDetailSerializer(qs, many=True)
    return Response(serializer.data)
