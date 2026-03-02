from django.urls import path
from .views import (
    RootView,
    RegisterView, 
    EligibilityView, 
    CreateLoanView, 
    ViewLoanDetailView, 
    ViewUserLoansView
)

urlpatterns = [
    path('', RootView.as_view(), name='root'),
    path('register', RegisterView.as_view(), name='register'),
    path('check-eligibility', EligibilityView.as_view(), name='check-eligibility'),
    path('create-loan', CreateLoanView.as_view(), name='create-loan'),
    path('view-loan/<int:loan_id>', ViewLoanDetailView.as_view(), name='view-loan'),
    path('view-loans/<int:customer_id>', ViewUserLoansView.as_view(), name='view-user-loans'),
]