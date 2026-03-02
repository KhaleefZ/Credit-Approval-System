from rest_framework import serializers
from .models import Customer, Loan

class RegisterSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    age = serializers.IntegerField()
    monthly_income = serializers.IntegerField()
    phone_number = serializers.IntegerField()
    
    def create(self, validated_data):
        # Map monthly_income to monthly_salary for the model
        validated_data['monthly_salary'] = validated_data.pop('monthly_income')
        return Customer.objects.create(**validated_data)

class EligibilitySerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class LoanSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    tenure = serializers.IntegerField()
    interest_rate = serializers.FloatField()
    start_date = serializers.DateField(required=False)