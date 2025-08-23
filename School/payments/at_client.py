import os
import africastalking

AT_USERNAME = os.getenv("AFRICASTALKING_USERNAME", "sandbox")
AT_API_KEY = os.getenv("AFRICASTALKING_API_KEY", "atsk_b17ffe277702d63f88a46132e9654eba26ab22f4f2173b43c9c5a50bdaea143079423ebd")

africastalking.initialize(username=AT_USERNAME, api_key=AT_API_KEY)

# Export SMS client
sms = africastalking.SMS
