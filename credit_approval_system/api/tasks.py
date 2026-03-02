import pandas as pd
from celery import shared_task
from .models import Customer, Loan

@shared_task
def ingest_data():
    """Ingest customer and loan data from Excel files"""
    
    # Ingest Customers
    print("Loading customer data...")
    cust_df = pd.read_excel('data/customer_data.xlsx')
    
    for _, row in cust_df.iterrows():
        # approved_limit = 36 * monthly_salary rounded to nearest lakh
        monthly_sal = row['Monthly Salary']
        limit = round((36 * monthly_sal) / 100000) * 100000
        
        Customer.objects.update_or_create(
            customer_id=row['Customer ID'],
            defaults={
                'first_name': row['First Name'],
                'last_name': row['Last Name'],
                'age': row['Age'],
                'phone_number': int(row['Phone Number']),
                'monthly_salary': monthly_sal,
                'approved_limit': limit,
                'current_debt': 0  # Not in Excel, defaulting to 0
            }
        )
    print(f"Ingested {len(cust_df)} customers")

    # Ingest Loans
    print("Loading loan data...")
    loan_df = pd.read_excel('data/loan_data.xlsx')
    
    for _, row in loan_df.iterrows():
        # Parse dates
        start_date = pd.to_datetime(row['Date of Approval']).date()
        end_date = pd.to_datetime(row['End Date']).date()
        
        Loan.objects.update_or_create(
            loan_id=row['Loan ID'],
            defaults={
                'customer_id': row['Customer ID'],
                'loan_amount': row['Loan Amount'],
                'tenure': row['Tenure'],
                'interest_rate': row['Interest Rate'],
                'monthly_repayment': row['Monthly payment'],
                'emis_paid_on_time': row['EMIs paid on Time'],
                'start_date': start_date,
                'end_date': end_date
            }
        )
    print(f"Ingested {len(loan_df)} loans")
    print("Data ingestion complete!")
    
    return f"Successfully ingested {len(cust_df)} customers and {len(loan_df)} loans"
