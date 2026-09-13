# Wi-Fi Billing System

A complete, production-ready billing and subscription management system for Wi-Fi hotspot services. Built with Flask, MySQL, and Streamlit.

## 📋 Features

- **User Management**: Secure registration and login with bcrypt password hashing
- **Subscription Management**: Create and manage flexible subscription plans
- **Payment Processing**: Record payments with multiple payment methods (M-Pesa, card, bank transfer, PayPal)
- **Usage Tracking**: Log and monitor data usage per subscription
- **Analytics Dashboard**: Real-time visualization of revenue, usage, and customer metrics
- **REST API**: Complete API for integration with other systems
- **JWT Authentication**: Secure API endpoints with token-based authentication
- **Streamlit Dashboard**: Interactive business intelligence dashboard

## 🏗️ Project Structure

```
billing_system/
├── app.py                 # Flask backend application with REST API
├── dashboard.py          # Streamlit analytics dashboard
├── config.py             # Configuration management
├── models.sql            # Database schema
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── templates/            # HTML frontend
│   ├── index.html       # Home page
│   ├── register.html    # Registration form
│   ├── login.html       # Login form
│   └── dashboard.html   # User dashboard
└── README.md            # This file
```

## 📊 Database Schema

### Users Table
```sql
- user_id (Primary Key)
- username (Unique)
- email (Unique)
- password_hash (Bcrypt hashed)
- phone_number
- status (active, inactive, suspended)
- created_at, updated_at (Timestamps)
```

### Subscriptions Table
```sql
- subscription_id (Primary Key)
- user_id (Foreign Key → Users)
- plan_name
- data_limit_gb
- monthly_price
- status (active, inactive, expired, cancelled)
- start_date, end_date, renewal_date
- created_at, updated_at
```

### Payments Table
```sql
- payment_id (Primary Key)
- subscription_id (Foreign Key → Subscriptions)
- amount
- payment_method
- transaction_ref
- status (success, failed, pending, refunded)
- payment_date
- created_at, updated_at
```

### Usage Logs Table
```sql
- usage_id (Primary Key)
- subscription_id (Foreign Key → Subscriptions)
- data_used_mb
- upload_mb, download_mb
- session_duration_minutes
- log_date (Timestamp)
```

## 🚀 Deployment Guide

### Prerequisites
- Python 3.8+
- MySQL 5.7+ or MariaDB
- pip (Python package manager)

### 1. Setup Database

#### Option A: Using MySQL Command Line
```bash
# Connect to MySQL
mysql -u root -p

# Run the SQL schema
source billing_system/models.sql
```

#### Option B: Using MySQL Workbench
1. Open MySQL Workbench
2. Create a new connection
3. Open the SQL file: `billing_system/models.sql`
4. Execute the script

### 2. Install Dependencies

```bash
# Navigate to project directory
cd billing_system

# Create virtual environment (optional but recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your database credentials
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

Update the following values:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=wifi_billing_system
SECRET_KEY=generate_a_random_secret_key
JWT_SECRET_KEY=generate_a_random_jwt_key
```

### 4. Run the Application

#### Backend (Flask API Server)

```bash
# Start Flask application
python app.py

# You should see:
# * Running on http://0.0.0.0:5000
# * Press CTRL+C to quit
```

The API will be available at: `http://localhost:5000`

#### Frontend (Access via Web Browser)

Open your browser and navigate to:
- **Home**: `http://localhost:5000/`
- **Register**: `http://localhost:5000/register`
- **Login**: `http://localhost:5000/login`
- **Dashboard**: `http://localhost:5000/dashboard` (after login)

#### Streamlit Dashboard (Analytics)

In a new terminal:

```bash
# Make sure you're in the billing_system directory
cd billing_system

# Start Streamlit
streamlit run dashboard.py

# You should see:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
```

## 📡 API Endpoints

### Authentication

#### Register User
```http
POST /api/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "phone_number": "+1234567890"
}

Response: 201 Created
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

#### Login
```http
POST /api/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "securepassword123"
}

Response: 200 OK
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user_id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "token": "eyJ0eXAiOiJKV1QiLC..."
  }
}
```

### Subscriptions

#### Create Subscription
```http
POST /api/subscribe
Authorization: Bearer <token>
Content-Type: application/json

{
  "plan_name": "Premium Plan",
  "data_limit_gb": 50,
  "monthly_price": 49.99
}

Response: 201 Created
{
  "success": true,
  "message": "Subscription created successfully",
  "data": {
    "subscription_id": 1,
    "user_id": 1,
    "plan_name": "Premium Plan",
    "data_limit_gb": 50,
    "monthly_price": 49.99,
    "status": "active"
  }
}
```

### Payments

#### Record Payment
```http
POST /api/payment
Authorization: Bearer <token>
Content-Type: application/json

{
  "subscription_id": 1,
  "amount": 49.99,
  "payment_method": "mpesa",
  "transaction_ref": "TXN-12345"
}

Response: 201 Created
{
  "success": true,
  "message": "Payment recorded successfully",
  "data": {
    "payment_id": 1,
    "subscription_id": 1,
    "amount": 49.99,
    "payment_method": "mpesa",
    "status": "success"
  }
}
```

### Usage Logging

#### Log Data Usage
```http
POST /api/usage
Authorization: Bearer <token>
Content-Type: application/json

{
  "subscription_id": 1,
  "data_used_mb": 256.5,
  "upload_mb": 100,
  "download_mb": 156.5,
  "session_duration_minutes": 45
}

Response: 201 Created
{
  "success": true,
  "message": "Usage logged successfully",
  "data": {
    "usage_id": 1,
    "subscription_id": 1,
    "data_used_mb": 256.5,
    "upload_mb": 100,
    "download_mb": 156.5
  }
}
```

### Dashboard Analytics

#### Get Monthly Metrics
```http
GET /api/dashboard
Authorization: Bearer <token>

Response: 200 OK
{
  "success": true,
  "data": {
    "period": "2024-01-01 to 2024-01-31",
    "revenue": 2499.50,
    "usage_mb": 102400,
    "usage_gb": 100,
    "active_customers": 50,
    "churned_customers": 5
  }
}
```

### Health Check

```http
GET /api/health

Response: 200 OK
{
  "status": "healthy",
  "database": "connected"
}
```

## 🔐 Security Features

1. **Password Security**
   - Bcrypt hashing with 12 salt rounds
   - Passwords never stored in plain text
   - Secure password validation

2. **API Authentication**
   - JWT (JSON Web Tokens) for API security
   - Token expiration (default: 24 hours)
   - Authorization header validation

3. **Database Security**
   - SQL injection prevention via parameterized queries
   - Foreign key constraints
   - Transaction management

4. **CORS Protection**
   - Cross-Origin Resource Sharing configured
   - API accessible from web origins

## 📊 Streamlit Dashboard Features

- **Key Metrics**: Real-time revenue, usage, active customers, and churn
- **Revenue Analytics**: Daily revenue trends and payment method breakdown
- **Usage Analytics**: Daily usage trends and top data consumers
- **Customer Analytics**: Subscription status distribution and plan breakdown
- **Detailed Tables**: Payments, usage logs, subscriptions, and users
- **Date Range Filtering**: Select custom date ranges or predefined periods
- **Status Filtering**: Filter by subscription status

## 🔧 Troubleshooting

### Database Connection Error
```
Error connecting to database: (1045, "Access denied for user 'root'@'localhost'")
```
**Solution**: Check your `.env` file and ensure DB_USER, DB_PASSWORD, and DB_HOST are correct.

### Port Already in Use
```
OSError: [Errno 10048] Only one usage of each socket address
```
**Solution**: Change the port in `.env` or kill the process using the port:
```bash
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :5000
kill -9 <PID>
```

### Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```
**Solution**: Ensure you activated the virtual environment and installed dependencies:
```bash
pip install -r requirements.txt
```

## 📈 Performance Optimization

1. **Database Indexes**: All tables include indexes on frequently queried columns
2. **Connection Pooling**: Database connections are efficiently managed
3. **JWT Caching**: Tokens are validated without database queries
4. **Pagination**: Large datasets use pagination to reduce memory usage

## 🚀 Deployment to Production

### Using Gunicorn (Recommended)

```bash
# Install Gunicorn
pip install gunicorn

# Run Flask app with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker (Optional)

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t wifi-billing-system .
docker run -p 5000:8501 -e DB_HOST=host.docker.internal wifi-billing-system
```

## 📚 Additional Notes

- The system uses UTC timestamps for all date/time fields
- All monetary amounts are stored as DECIMAL(10, 2)
- Data usage is tracked in MB and converted to GB for display
- Monthly revenue is calculated from successful payments only
- Customer churn is tracked via subscription status changes

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Flask and MySQL documentation
3. Check application logs in the terminal

## 📝 License

This project is provided as-is for educational and commercial use.

## 🎯 Next Steps

1. **Email Notifications**: Add email alerts for subscription renewals and low balance
2. **SMS Integration**: Send SMS notifications for payments and usage alerts
3. **Advanced Analytics**: Implement machine learning for churn prediction
4. **Mobile App**: Develop mobile applications for iOS and Android
5. **API Rate Limiting**: Implement advanced rate limiting per user
6. **Webhook Support**: Add webhook endpoints for third-party integrations
7. **Two-Factor Authentication**: Enhance security with 2FA
8. **Subscription Auto-Renewal**: Implement automatic subscription renewal

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready
