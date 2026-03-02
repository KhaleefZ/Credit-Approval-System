from django.test import TestCase
from rest_framework.test import APIClient
from .models import Customer

class CreditApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.customer = Customer.objects.create(
            first_name="Khaleef",
            last_name="Z",
            age=25,
            phone_number=9876543210,
            monthly_income=50000,
            approved_limit=1800000
        )

    def test_eligibility_check(self):
        data = {
            "customer_id": self.customer.customer_id,
            "loan_amount": 100000,
            "interest_rate": 10.0,
            "tenure": 12
        }
        response = self.client.post('/api/check-eligibility', data, format='json')
        self.assertEqual(response.status_code, 200)