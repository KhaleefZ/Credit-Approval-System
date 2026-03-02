# Credit Approval System

A Django-based REST API for managing credit approvals, customer registrations, loan eligibility checks, and loan management.

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
- [Running with Docker](#running-with-docker)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-aschema)
- [Features](#features)
- [Testing](#testing)
- [Project Structure](#project-structure)

---

## Overview

The Credit Approval System is designed to:
- Register and manage customer information
- Calculate credit scores based on loan history
- Check loan eligibility with interest rate adjustments
- Create and track loans
- Manage EMI (Equated Monthly Installment) payments
- Process background tasks using Celery workers

**Tech Stack:**
- Backend: Django 4.2 + Django REST Framework
- Database: PostgreSQL 15
- Cache/Broker: Redis
- Task Queue: Celery
- Container: Docker & Docker Compose

---

## Requirements

### System Requirements
- Docker
- Docker Compose
- macOS/Linux (or WSL2 on Windows)

### Python Packages
See `requirements.txt` for complete list:
- django>=4.0
- djangorestframework
- psycopg2-binary
- pandas
- openpyxl
- celery
- redis
- python-dotenv

---

## Setup Instructions

### 1. Navigate to Project Directory
```bash
cd "/Users/khaleef/Downloads/Assignment /Backend Internship Assignment/credit_approval_system"
```

### 2. Build and Start Docker Containers
```bash
docker-compose up --build
```

Wait for all services to start. You should see:
- PostgreSQL: "database system is ready to accept connections"
- Redis: "Ready to accept connections"
- Django Web: "Watching for file changes with StatReloader"
- Celery Worker: "celery@... ready"

### 3. Run Database Migrations
In a new terminal:
```bash
docker-compose exec web python manage.py migrate
```

Expected output:
```
Running migrations:
  Applying admin.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying api.0001_initial... OK
  ...
```

### 4. Create Admin User (Optional)
```bash
docker-compose exec web python manage.py createsuperuser
```

Follow the prompts to create your admin credentials.

### 5. Load Initial Data (Optional)
To ingest customer and loan data from Excel files:
```bash
docker-compose exec web python manage.py shell

# Then in the Django shell:
from api.tasks import ingest_data
ingest_data()

# Or trigger via Celery:
from api.tasks import ingest_data
ingest_data.delay()
```

---

## Running with Docker

### Start Services
```bash
docker-compose up --build
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Reset Database)
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs web
docker-compose logs worker
docker-compose logs db
```

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Django API | http://localhost:8000 | REST API |
| Django Admin | http://localhost:8000/admin | Admin panel |
| PostgreSQL | localhost:5432 | Database |
| Redis | localhost:6379 | Cache/Broker |

---

## API Endpoints

### Base URL
```
http://localhost:8000/api/
```

### 1. **Register Customer** (POST)
Create a new customer account.

**Endpoint:** `/api/register`

**Request:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "age": 30,
  "monthly_salary": 50000,
  "phone_number": "9876543210",
  "email": "john@example.com"
}
```

**Response (201 Created):**
```json
{
  "customer_id": 1,
  "name": "John Doe",
  "approved_limit": 1800000
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"first_name":"John","last_name":"Doe","age":30,"monthly_salary":50000,"phone_number":"9876543210","email":"john@example.com"}'
```

---

### 2. **Check Loan Eligibility** (POST)
Check if a customer is eligible for a loan and get the corrected interest rate.

**Endpoint:** `/api/check-eligibility`

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10,
  "tenure": 24
}
```

**Response (200 OK):**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10,
  "corrected_interest_rate": 10,
  "tenure": 24,
  "monthly_installment": 21875.00
}
```

**Credit Score Rules:**
- Score > 50: Approved at requested rate
- Score 30-50: Approved, minimum 12% interest rate
- Score 10-30: Approved, minimum 16% interest rate
- Score < 10: Rejected

**cURL:**
```bash
curl -X POST http://localhost:8000/api/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"loan_amount":500000,"interest_rate":10,"tenure":24}'
```

---

### 3. **Create Loan** (POST)
Create a new loan for an approved customer.

**Endpoint:** `/api/create-loan`

**Request:**
```json
{
  "customer_id": 1,
  "loan_amount": 500000,
  "interest_rate": 10,
  "tenure": 24,
  "start_date": "2026-03-01"
}
```

**Response (201 Created):**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_amount": 500000,
  "tenure": 24,
  "interest_rate": 10,
  "monthly_repayment": 21875.00
}
```

**cURL:**
```bash
curl -X POST http://localhost:8000/api/create-loan \
  -H "Content-Type: application/json" \
  -d '{"customer_id":1,"loan_amount":500000,"interest_rate":10,"tenure":24,"start_date":"2026-03-01"}'
```

---

### 4. **View Loan Details** (GET)
Get details of a specific loan.

**Endpoint:** `/api/view-loan/<loan_id>`

**Response (200 OK):**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_amount": 500000,
  "tenure": 24,
  "interest_rate": 10,
  "monthly_repayment": 21875.00,
  "emis_paid_on_time": 0,
  "status": "active"
}
```

**cURL:**
```bash
curl http://localhost:8000/api/view-loan/1
```

---

### 5. **View Customer Loans** (GET)
Get all loans for a specific customer.

**Endpoint:** `/api/view-loans/<customer_id>`

**Response (200 OK):**
```json
{
  "customer_loans": [
    {
      "loan_id": 1,
      "loan_amount": 500000,
      "tenure": 24,
      "interest_rate": 10,
      "monthly_repayment": 21875.00,
      "status": "active"
    }
  ]
}
```

**cURL:**
```bash
curl http://localhost:8000/api/view-loans/1
```

---

## Database Schema

### Customer Table
| Column | Type | Constraints |
|--------|------|-------------|
| customer_id | AutoField | Primary Key |
| first_name | CharField | Max 100 |
| last_name | CharField | Max 100 |
| age | IntegerField | |
| phone_number | BigIntegerField | |
| monthly_salary | IntegerField | |
| approved_limit | IntegerField | (36 × salary) rounded to nearest lakh |
| current_debt | IntegerField | Default 0 |
| email | EmailField | Optional |

### Loan Table
| Column | Type | Constraints |
|--------|------|-------------|
| loan_id | AutoField | Primary Key |
| customer | ForeignKey | References Customer |
| loan_amount | FloatField | |
| tenure | IntegerField | In months |
| interest_rate | FloatField | Annual percentage |
| monthly_repayment | FloatField | EMI amount |
| emis_paid_on_time | IntegerField | Count of on-time EMIs |
| start_date | DateField | |
| end_date | DateField | |

---

## Features

✅ **Customer Management**
- Register new customers
- Store customer financial information
- Calculate approved credit limit based on salary

✅ **Credit Scoring**
- Calculate credit score based on loan history
- Consider on-time payment ratio
- Track loan activity

✅ **Loan Eligibility**
- Check loan approval status
- Adjust interest rates based on credit score
- Validate EMI against income limits
- Calculate monthly installments

✅ **Loan Management**
- Create loans for approved customers
- Track loan details
- Record EMI payments
- View loan history

✅ **Background Tasks**
- Celery workers for async operations
- Data ingestion from Excel files
- Task queue management with Redis

✅ **API Documentation**
- Browsable API with DRF
- Comprehensive API endpoints
- Error handling and validation

✅ **Admin Panel**
- Django admin interface
- Manage customers and loans
- View data through admin dashboard

---

## Testing

### Test Case 1: Register Customer
```bash
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Alice",
    "last_name": "Smith",
    "age": 28,
    "monthly_salary": 75000,
    "phone_number": "9999999999",
    "email": "alice@example.com"
  }'
```

### Test Case 2: Check Eligibility
```bash
curl -X POST http://localhost:8000/api/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 750000,
    "interest_rate": 12,
    "tenure": 36
  }'
```

### Test Case 3: Create Loan
```bash
curl -X POST http://localhost:8000/api/create-loan \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "loan_amount": 750000,
    "interest_rate": 12,
    "tenure": 36
  }'
```

### Test Case 4: View Loan
```bash
curl http://localhost:8000/api/view-loan/1
```

### Test Case 5: View Customer Loans
```bash
curl http://localhost:8000/api/view-loans/1
```

### Test Error Cases
```bash
# Invalid customer
curl http://localhost:8000/api/view-loan/999

# Missing required fields
curl -X POST http://localhost:8000/api/register \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Test"}'
```

### Access Admin Panel
1. Navigate to: http://localhost:8000/admin/
2. Login with superuser credentials
3. View and manage:
   - Customers
   - Loans

---

## Project Structure

```
credit_approval_system/
├── api/                              # Main API application
│   ├── migrations/                   # Database migrations
│   ├── __init__.py
│   ├── admin.py                      # Django admin configuration
│   ├── apps.py
│   ├── models.py                     # Database models
│   ├── views.py                      # API views
│   ├── serializers.py                # DRF serializers
│   ├── services.py                   # Business logic
│   ├── tasks.py                      # Celery tasks
│   ├── tests.py
│   └── urls.py                       # API routes
├── core/                             # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py                     # Celery configuration
│   ├── settings.py                   # Django settings
│   ├── urls.py                       # Project URLs
│   └── wsgi.py
├── data/                             # Excel data files
│   ├── customer_data.xlsx
│   └── loan_data.xlsx
├── Dockerfile                        # Docker configuration
├── docker-compose.yml                # Docker Compose configuration
├── requirements.txt                  # Python dependencies
├── manage.py                         # Django CLI
├── db.sqlite3                        # SQLite database (dev only)
└── README.md                         # This file
```

---

## Configuration

### Environment Variables
Create a `.env` file if needed:
```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@db:5432/credit_db

# Redis
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

### Django Settings
- Location: `core/settings.py`
- Database: PostgreSQL (via Docker)
- Cache: Redis
- Task Queue: Celery with Redis broker

---

## Common Commands

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access Django shell
docker-compose exec web python manage.py shell

# Run tests
docker-compose exec web python manage.py test

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# View logs
docker-compose logs -f web
docker-compose logs -f worker
docker-compose logs -f db

# Check Celery tasks
docker-compose exec web python manage.py shell
# Then: from api.tasks import ingest_data; ingest_data()
```

---

## Troubleshooting

### Issue: Cannot connect to database
**Solution:** Ensure PostgreSQL container is running
```bash
docker-compose ps
docker-compose restart db
```

### Issue: Celery worker not connecting to Redis
**Solution:** Check Redis container and restart services
```bash
docker-compose logs redis
docker-compose restart redis worker
```

### Issue: Port 8000 already in use
**Solution:** Stop the service using the port or use a different port
```bash
docker-compose down
# Or modify docker-compose.yml port mapping
```

### Issue: Database migration errors
**Solution:** Reset database and reapply migrations
```bash
docker-compose down -v
docker-compose up --build
docker-compose exec web python manage.py migrate
```

---

## Performance Optimization

- **Database Indexing:** customer_id and loan_id are indexed as primary keys
- **Caching:** Redis stores frequently accessed data
- **Async Tasks:** Celery handles background operations
- **Query Optimization:** Use select_related/prefetch_related when needed

---

## Security Notes

⚠️ **For Development Only:**
- DEBUG=True in settings
- Secret key should be changed in production
- Update ALLOWED_HOSTS for production
- Use environment variables for sensitive data

---

## Version Info

- Django: 4.2+
- Python: 3.10
- PostgreSQL: 15
- Redis: 7
- Django REST Framework: Latest

---

## Support & Documentation

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

---

## License

This project is part of the Backend Internship Assignment.

---

## Author Notes

This system implements:
- RESTful API design principles
- Proper error handling and validation
- Database relationships and constraints
- Async task processing
- Credit scoring algorithms
- Interest rate adjustments based on credit history

All requirements from the assignment specification have been implemented and tested.

---
