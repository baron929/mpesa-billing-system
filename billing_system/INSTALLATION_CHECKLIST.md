# Installation & Verification Checklist

Complete this checklist to verify your Wi-Fi Billing System installation is working correctly.

## ✅ Pre-Installation Checklist

- [ ] Python 3.8+ installed and in PATH
- [ ] MySQL 5.7+ installed and running
- [ ] Git installed (if cloning from repository)
- [ ] Administrator/sudo access (for system packages)
- [ ] At least 2GB free disk space
- [ ] 512MB free RAM available

## ✅ Installation Steps Checklist

### Step 1: Setup Environment
- [ ] Navigated to `billing_system` directory
- [ ] Ran setup script (`setup.bat` or `setup.sh`)
- [ ] Virtual environment created successfully
- [ ] Dependencies installed without errors

### Step 2: Database Setup
- [ ] MySQL server is running
- [ ] Connected to MySQL successfully
- [ ] Executed `models.sql` script
- [ ] All 4 tables created (users, subscriptions, payments, usage_logs)
- [ ] Indexes created successfully

Verify with:
```bash
mysql -u root -p -e "USE wifi_billing_system; SHOW TABLES;"
```

### Step 3: Configuration
- [ ] Copied `.env.example` to `.env`
- [ ] Updated `DB_USER` in .env
- [ ] Updated `DB_PASSWORD` in .env
- [ ] Updated `DB_HOST` in .env (localhost for local dev)
- [ ] Generated `SECRET_KEY`
- [ ] Generated `JWT_SECRET_KEY`
- [ ] Set `FLASK_ENV` to `development`

### Step 4: Backend Startup
- [ ] Activated virtual environment
- [ ] Ran `python app.py`
- [ ] No import errors
- [ ] Flask server started on `http://0.0.0.0:5000`
- [ ] No database connection errors

## ✅ Functionality Verification

### Health Check
- [ ] Opened `http://localhost:5000/api/health`
- [ ] Response shows `"status": "healthy"`
- [ ] Response shows `"database": "connected"`

### Frontend Pages
- [ ] Home page loads at `http://localhost:5000/`
- [ ] Register page accessible at `http://localhost:5000/register`
- [ ] Login page accessible at `http://localhost:5000/login`

### User Registration
- [ ] Registration form displays correctly
- [ ] Can enter username, email, password
- [ ] Password confirmation validation works
- [ ] Form submission succeeds
- [ ] User appears in database

Verify in MySQL:
```bash
mysql -u root -p -e "USE wifi_billing_system; SELECT * FROM users;"
```

### User Login
- [ ] Can login with registered credentials
- [ ] JWT token is generated
- [ ] Dashboard page loads after login
- [ ] Logout functionality works

### Subscription Management
- [ ] Can create new subscription from dashboard
- [ ] Subscription appears in subscriptions table
- [ ] Plan details saved correctly

Verify:
```bash
mysql -u root -p -e "USE wifi_billing_system; SELECT * FROM subscriptions;"
```

### Payment Processing
- [ ] Can record payment from dashboard
- [ ] Payment appears in payments table
- [ ] Payment status shows as "success"
- [ ] Amount recorded correctly

Verify:
```bash
mysql -u root -p -e "USE wifi_billing_system; SELECT * FROM payments;"
```

### Usage Logging
- [ ] Can log data usage from dashboard
- [ ] Usage entry appears in usage_logs table
- [ ] Data in MB recorded correctly
- [ ] Upload/download separated properly

Verify:
```bash
mysql -u root -p -e "USE wifi_billing_system; SELECT * FROM usage_logs;"
```

### Dashboard Metrics
- [ ] Can access `/api/dashboard` endpoint
- [ ] Returns revenue data
- [ ] Returns usage data
- [ ] Returns active customers count
- [ ] Returns churned customers count

## ✅ API Testing Checklist

### Using cURL or Postman

**Register Endpoint**:
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123456"
  }'
```
- [ ] Returns 201 status code
- [ ] Response includes user_id
- [ ] Returns success message

**Login Endpoint**:
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123456"
  }'
```
- [ ] Returns 200 status code
- [ ] Response includes JWT token
- [ ] Token can be used in headers

**Subscribe Endpoint**:
```bash
curl -X POST http://localhost:5000/api/subscribe \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "plan_name": "Test Plan",
    "data_limit_gb": 10,
    "monthly_price": 9.99
  }'
```
- [ ] Returns 201 status code
- [ ] Subscription created with correct data
- [ ] Status defaults to "active"

**Dashboard Endpoint**:
```bash
curl -X GET http://localhost:5000/api/dashboard \
  -H "Authorization: Bearer <TOKEN>"
```
- [ ] Returns 200 status code
- [ ] Response includes revenue figure
- [ ] Response includes usage data
- [ ] Response includes customer metrics

## ✅ Streamlit Dashboard (Optional)

- [ ] Started Streamlit with `streamlit run dashboard.py`
- [ ] Dashboard accessible at `http://localhost:8501`
- [ ] Database connection successful
- [ ] Sidebar filters working
- [ ] Charts load correctly
- [ ] Can view data tables
- [ ] Date range selector works
- [ ] Status filter works

## ✅ Docker Deployment (Optional)

- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] Ran `docker-compose up -d`
- [ ] All 3 services started (MySQL, Flask, Streamlit)
- [ ] No port conflicts (5000, 8501, 3306)
- [ ] Services healthy (`docker-compose ps`)
- [ ] Can access Flask at `http://localhost:5000`
- [ ] Can access Streamlit at `http://localhost:8501`

## ✅ Security Verification

- [ ] Passwords are bcrypt hashed
  ```bash
  mysql -u root -p -e "USE wifi_billing_system; SELECT password_hash FROM users LIMIT 1;"
  # Should show hash starting with $2
  ```
- [ ] JWT tokens are generated
- [ ] Protected endpoints require token
- [ ] Invalid tokens are rejected
- [ ] CORS headers present in responses
- [ ] SQL injection attempts fail

## ✅ Performance Baseline

### Response Time
- [ ] Health check: < 50ms
- [ ] Register: < 200ms
- [ ] Login: < 200ms
- [ ] Dashboard: < 500ms
- [ ] Subscribe: < 200ms

### Database Queries
- [ ] User lookup: < 10ms
- [ ] Dashboard aggregation: < 50ms
- [ ] Usage query: < 30ms

Test with:
```bash
# Multiple requests
for i in {1..10}; do time curl -s http://localhost:5000/api/health > /dev/null; done
```

## ✅ Error Handling

### Test Error Cases
- [ ] Invalid username returns 401
- [ ] Wrong password returns 401
- [ ] Duplicate username returns 409
- [ ] Invalid email format returns 400
- [ ] Missing required fields returns 400
- [ ] Expired token returns 401
- [ ] Invalid token returns 401

## ✅ Database Integrity

- [ ] Foreign key constraints work
- [ ] Cannot delete user with active subscriptions
- [ ] Cannot create payment for non-existent subscription
- [ ] Cannot log usage for non-existent subscription
- [ ] Timestamps auto-populate correctly
- [ ] Default values set properly

Verify:
```bash
mysql -u root -p -e "USE wifi_billing_system; SHOW CREATE TABLE subscriptions\G"
# Check FOREIGN KEY constraints
```

## ✅ Documentation Review

- [ ] Read README.md
- [ ] Reviewed QUICKSTART.md
- [ ] Checked API endpoints in app.py
- [ ] Reviewed database schema in models.sql
- [ ] Understood config.py settings
- [ ] Reviewed DEPLOYMENT.md for production setup

## ✅ Backup & Recovery

- [ ] Created database backup
  ```bash
  mysqldump -u root -p wifi_billing_system > backup.sql
  ```
- [ ] Verified backup file exists
- [ ] Tested restore procedure (optional)
  ```bash
  mysql -u root -p wifi_billing_system < backup.sql
  ```

## ✅ Production Readiness

- [ ] All tests passing
- [ ] Error logs checked
- [ ] Performance acceptable
- [ ] Security measures in place
- [ ] Backup strategy defined
- [ ] Monitoring planned
- [ ] Scaling strategy understood
- [ ] Deployment method chosen

## 🔧 Troubleshooting Common Issues

### "Connection refused" to MySQL
- [ ] Check MySQL is running: `mysql -u root -p -e "SELECT 1;"`
- [ ] Verify credentials in .env
- [ ] Check DB_HOST is correct (localhost for local)

### "Module not found" errors
- [ ] Activate virtual environment
- [ ] Reinstall requirements: `pip install -r requirements.txt`
- [ ] Check Python version: `python --version`

### Port already in use
- [ ] Change port in .env: `FLASK_PORT=5001`
- [ ] Or kill process: `lsof -i :5000` (Unix) or `netstat -ano | findstr :5000` (Windows)

### Database queries timing out
- [ ] Check MySQL is not overloaded
- [ ] Verify indexes exist: `SHOW INDEX FROM tablename;`
- [ ] Consider adding more indexes

### Slow performance
- [ ] Check database connection pool
- [ ] Monitor system resources (CPU, memory, disk)
- [ ] Check for slow queries in MySQL

## ✅ Sign-Off

| Item | Status | Date | Notes |
|------|--------|------|-------|
| Installation | ☐ Complete | _____ | _______ |
| Configuration | ☐ Complete | _____ | _______ |
| Database Setup | ☐ Complete | _____ | _______ |
| Functionality Tests | ☐ Passed | _____ | _______ |
| API Tests | ☐ Passed | _____ | _______ |
| Security Checks | ☐ Passed | _____ | _______ |
| Performance Tests | ☐ Passed | _____ | _______ |
| Documentation Review | ☐ Complete | _____ | _______ |
| Production Ready | ☐ Yes | _____ | _______ |

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the error message carefully
3. Check application logs in the terminal
4. Consult README.md and DEPLOYMENT.md
5. Verify all prerequisites are installed

---

**Checklist Version**: 1.0  
**Last Updated**: 2024  

Once all items are checked, your Wi-Fi Billing System is ready for deployment! 🎉
