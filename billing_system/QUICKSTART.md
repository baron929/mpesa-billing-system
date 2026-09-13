# Quick Start Guide

Get the Wi-Fi Billing System running in 5 minutes!

## Prerequisites
- Python 3.8+
- MySQL 5.7+
- Git

## 🚀 Quick Start (Windows)

### Step 1: Run Setup
```bash
cd billing_system
setup.bat
```

### Step 2: Configure Database
```bash
# Open MySQL Command Line or Workbench and run:
source billing_system/models.sql

# Or from command line:
mysql -u root -p < billing_system/models.sql
```

### Step 3: Update Environment
```bash
# Edit .env with your database credentials
notepad .env
```

Update these values:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=wifi_billing_system
```

### Step 4: Start Backend
```bash
# In PowerShell or Command Prompt
cd billing_system
venv\Scripts\activate
python app.py
```

You should see:
```
 * Running on http://0.0.0.0:5000
```

### Step 5: Start Dashboard (Optional)
```bash
# In a new terminal
cd billing_system
venv\Scripts\activate
streamlit run dashboard.py
```

## 🌐 Access the Application

| Component | URL | Purpose |
|-----------|-----|---------|
| **Home Page** | http://localhost:5000 | Welcome page |
| **Register** | http://localhost:5000/register | Create account |
| **Login** | http://localhost:5000/login | Access dashboard |
| **Dashboard** | http://localhost:5000/dashboard | User dashboard |
| **API Docs** | http://localhost:5000/api | REST API |
| **Analytics** | http://localhost:8501 | Streamlit dashboard |

## 📱 Test the System

### 1. Register a User
1. Go to http://localhost:5000/register
2. Fill in:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `Test123!@#`
   - Phone (optional): `+1234567890`
3. Click "Create Account"

### 2. Login
1. Go to http://localhost:5000/login
2. Enter credentials from above
3. Click "Login"

### 3. Create a Subscription
1. On dashboard, click "Add New" under Subscription Management
2. Fill in:
   - Plan Name: `Basic Plan`
   - Data Limit: `10` GB
   - Monthly Price: `9.99` $
3. Click "Create Subscription"

### 4. Log Usage
1. Click "Log Usage" tab
2. Fill in:
   - Select Subscription: (your subscription)
   - Data Used: `100` MB
   - Download: `80` MB
   - Upload: `20` MB
   - Duration: `30` minutes
3. Click "Log Usage"

### 5. Make Payment
1. Click "Make Payment" tab
2. Fill in:
   - Select Subscription: (your subscription)
   - Amount: `9.99` $
   - Payment Method: M-Pesa (or other)
3. Click "Process Payment"

## 🔌 Test REST API

### Using cURL or Postman

**1. Register:**
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**2. Login:**
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123"
  }'
```

**3. Save the token from response and use it:**
```bash
TOKEN="eyJ0eXAiOiJKV1QiLC..."

curl -X POST http://localhost:5000/api/subscribe \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "Premium",
    "data_limit_gb": 50,
    "monthly_price": 49.99
  }'
```

**4. Record Payment:**
```bash
curl -X POST http://localhost:5000/api/payment \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": 1,
    "amount": 49.99,
    "payment_method": "mpesa"
  }'
```

**5. Log Usage:**
```bash
curl -X POST http://localhost:5000/api/usage \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "subscription_id": 1,
    "data_used_mb": 256,
    "download_mb": 200,
    "upload_mb": 56,
    "session_duration_minutes": 45
  }'
```

**6. Get Dashboard Metrics:**
```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

**7. Health Check:**
```bash
curl http://localhost:5000/api/health
```

## 📊 View Streamlit Dashboard

1. Start Streamlit (see Step 5 above)
2. Open http://localhost:8501
3. Browse analytics:
   - Daily revenue trends
   - Data usage patterns
   - Active customers
   - Payment history
   - Usage logs

## 🐛 Troubleshooting

### "Access denied for user 'root'@'localhost'"
- Update DB_PASSWORD in .env to match your MySQL password
- Ensure MySQL server is running

### "Module not found" error
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Port 5000 already in use
- Change port in .env: `FLASK_PORT=5001`
- Or kill process using port: `netstat -ano | findstr :5000`

### Database connection timeout
- Check MySQL is running: `mysql -u root -p`
- Verify credentials in .env
- Check firewall settings

## 📚 Next Steps

1. **Read Full Documentation**: See [README.md](README.md)
2. **Production Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
3. **API Reference**: Check [app.py](app.py) endpoints
4. **Database Schema**: Review [models.sql](models.sql)
5. **Configuration**: Edit [config.py](config.py)

## 💡 Tips

- Use `localhost` instead of `127.0.0.1` if you have issues
- Keep both Flask and Streamlit terminals visible for logs
- Use browser DevTools (F12) to check API requests
- Check console output for detailed error messages
- Enable DEBUG mode in .env for more verbose logging

## 🆘 Need Help?

1. Check the terminal output for error messages
2. Review logs in the terminal
3. Check the FAQ section in README.md
4. Verify all prerequisites are installed
5. Try restarting the services

---

**Happy Coding!** 🎉

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md).
