from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .services import get_eligibility
from .serializers import RegisterSerializer, EligibilitySerializer, LoanSerializer
from datetime import timedelta

class RootView(APIView):
    def get(self, request):
        return Response({
            "message": "Credit Approval System API",
            "endpoints": {
                "register": {
                    "method": "POST",
                    "url": "/api/register",
                    "description": "Register a new customer"
                },
                "check-eligibility": {
                    "method": "POST",
                    "url": "/api/check-eligibility",
                    "description": "Check loan eligibility"
                },
                "create-loan": {
                    "method": "POST",
                    "url": "/api/create-loan",
                    "description": "Create a new loan"
                },
                "view-loan": {
                    "method": "GET",
                    "url": "/api/view-loan/<loan_id>",
                    "description": "View specific loan details"
                },
                "view-loans": {
                    "method": "GET",
                    "url": "/api/view-loans/<customer_id>",
                    "description": "View all loans for a customer"
                },
                "admin": {
                    "url": "/admin/",
                    "description": "Django admin panel"
                }
            }
        })

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            # monthly_income in request maps to monthly_salary in model
            income = serializer.validated_data['monthly_income']
            limit = round((36 * income) / 100000) * 100000
            
            # Create customer with proper field mapping
            customer = Customer.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                age=serializer.validated_data['age'],
                phone_number=serializer.validated_data['phone_number'],
                monthly_salary=income,
                approved_limit=limit
            )
            
            return Response({
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": customer.monthly_salary,
                "approved_limit": limit,
                "phone_number": customer.phone_number
            }, status=201)
        return Response(serializer.errors, status=400)

class EligibilityView(APIView):
    def post(self, request):
        customer = Customer.objects.get(customer_id=request.data['customer_id'])
        approved, rate, emi = get_eligibility(
            customer, 
            request.data['loan_amount'], 
            request.data['interest_rate'], 
            request.data['tenure']
        )
        return Response({
            "customer_id": customer.customer_id,
            "approval": approved,
            "interest_rate": request.data['interest_rate'],
            "corrected_interest_rate": rate,
            "tenure": request.data['tenure'],
            "monthly_installment": emi
        })

class CreateLoanView(APIView):
    def post(self, request):
        serializer = LoanSerializer(data=request.data)
        if serializer.is_valid():
            customer = Customer.objects.get(customer_id=serializer.validated_data['customer_id'])
            loan_amount = serializer.validated_data['loan_amount']
            tenure = serializer.validated_data['tenure']
            interest_rate = serializer.validated_data['interest_rate']
            
            # Check eligibility
            approved, corrected_rate, monthly_installment = get_eligibility(
                customer, loan_amount, interest_rate, tenure
            )
            
            if not approved:
                return Response({
                    "loan_id": None,
                    "customer_id": customer.customer_id,
                    "loan_approved": False,
                    "message": "Loan cannot be approved based on credit score or EMI constraints",
                    "monthly_installment": 0
                }, status=status.HTTP_200_OK)
            
            # Create loan with corrected interest rate
            from datetime import date
            start_date = serializer.validated_data.get('start_date', date.today())
            end_date = start_date + timedelta(days=tenure*30)
            
            loan = Loan.objects.create(
                customer=customer,
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_rate,
                monthly_repayment=monthly_installment,
                emis_paid_on_time=0,
                start_date=start_date,
                end_date=end_date
            )
            
            return Response({
                "loan_id": loan.loan_id,
                "customer_id": customer.customer_id,
                "loan_approved": True,
                "message": "Loan approved successfully",
                "monthly_installment": round(monthly_installment, 2)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ViewLoanDetailView(APIView):
    def get(self, request, loan_id):
        try:
            loan = Loan.objects.get(loan_id=loan_id)
            return Response({
                "loan_id": loan.loan_id,
                "customer": {
                    "id": loan.customer.customer_id,
                    "first_name": loan.customer.first_name,
                    "last_name": loan.customer.last_name,
                    "phone_number": loan.customer.phone_number,
                    "age": loan.customer.age
                },
                "loan_amount": loan.loan_amount,
                "interest_rate": loan.interest_rate,
                "monthly_installment": loan.monthly_repayment,
                "tenure": loan.tenure
            })
        except Loan.DoesNotExist:
            return Response({
                "error": "Loan not found"
            }, status=status.HTTP_404_NOT_FOUND)

class ViewUserLoansView(APIView):
    def get(self, request, customer_id):
        try:
            customer = Customer.objects.get(customer_id=customer_id)
            loans = Loan.objects.filter(customer=customer)
            loans_data = []
            for loan in loans:
                repayments_left = loan.tenure - loan.emis_paid_on_time
                loans_data.append({
                    "loan_id": loan.loan_id,
                    "loan_amount": loan.loan_amount,
                    "interest_rate": loan.interest_rate,
                    "monthly_installment": loan.monthly_repayment,
                    "repayments_left": repayments_left
                })
            return Response(loans_data)
        except Customer.DoesNotExist:
            return Response({
                "error": "Customer not found"
            }, status=status.HTTP_404_NOT_FOUND)