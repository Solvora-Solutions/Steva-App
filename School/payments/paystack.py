import requests
from django.conf import settings

class Paystack:
    base_url = "https://api.paystack.co"

    def __init__(self):
        try:
            self.secret_key = settings.PAYSTACK_SECRET_KEY
        except AttributeError:
            raise RuntimeError("PAYSTACK_SECRET_KEY is not set in settings.py")

    def initialize_transaction(self, email: str, amount_pesewas: int, callback_url: str, reference: str = None):
        """
        Initialize a transaction on Paystack.
        amount_pesewas: integer amount in pessewas (smallest currency unit).
        Returns the JSON response from Paystack.
        """
        url = f"{self.base_url}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "email": email,
            "amount": amount_pesewas,
            "callback_url": callback_url
        }
        if reference:
            payload["reference"] = reference

        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def verify_transaction(self, reference: str):
        """
        Verify a transaction using its reference.
        Returns the JSON response from Paystack.
        """
        url = f"{self.base_url}/transaction/verify/{reference}"
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()
