from django.urls import path
from . import views

urlpatterns = [
    path('initialize/', views.initialize_payment, name='payments-initialize'),
    path('verify/<str:reference>/', views.verify_payment, name='payments-verify'),
    path('my-payments/', views.list_my_payments, name='payments-my-payments'),
]