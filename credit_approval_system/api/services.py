from datetime import date
from .models import Loan

def calculate_credit_score(customer):
    loans = Loan.objects.filter(customer=customer)
    score = 0
    
    # i. Past Loans paid on time (cite: 50)
    # ii. Number of loans taken in past (cite: 51)
    # iii. Loan activity in current year (cite: 53)
    # iv. Loan approved volume (cite: 55)
    
    # Example logic: points for on-time payments
    on_time_ratio = sum(l.emis_paid_on_time for l in loans) / (sum(l.tenure for l in loans) or 1)
    score += on_time_ratio * 50
    
    # v. If sum of current loans > approved limit, score = 0 (cite: 57)
    total_active_loan = sum(l.loan_amount for l in loans)
    if total_active_loan > customer.approved_limit:
        return 0
        
    return min(score, 100)

def get_eligibility(customer, loan_amount, interest_rate, tenure):
    score = calculate_credit_score(customer)
    corrected_rate = interest_rate
    approved = False
    
    # Monthly EMI Check (Current + New) (cite: 64)
    # New EMI Calculation using Compound Interest (cite: 38)
    r = interest_rate / 1200
    new_emi = (loan_amount * r * (1+r)**tenure) / ((1+r)**tenure - 1)
    
    total_emis = sum(l.monthly_repayment for l in Loan.objects.filter(customer=customer)) + new_emi
    if total_emis > (0.5 * customer.monthly_salary):
        return False, interest_rate, new_emi

    # Slab checks (cite: 59-63)
    if score > 50:
        approved = True
    elif 50 > score > 30:
        approved = True
        corrected_rate = max(interest_rate, 12.0)  # cite: 61
    elif 30 > score > 10:
        approved = True
        corrected_rate = max(interest_rate, 16.0)  # cite: 62
    else:
        approved = False  # cite: 63
        
    return approved, corrected_rate, new_emi