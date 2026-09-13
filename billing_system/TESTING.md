# Testing Guide

Comprehensive testing guide for the Wi-Fi Billing System.

## Table of Contents
1. [Unit Testing](#unit-testing)
2. [Integration Testing](#integration-testing)
3. [API Testing](#api-testing)
4. [Performance Testing](#performance-testing)
5. [Security Testing](#security-testing)

## Unit Testing

Create a `test_app.py` file:

```python
import unittest
import json
from app import app
import os

class TestWiFiBillingAPI(unittest.TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        self.token = None
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
    
    def test_register_user(self):
        """Test user registration"""
        response = self.client.post('/api/register',
            data=json.dumps({
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'TestPass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
    
    def test_login_user(self):
        """Test user login"""
        # First register
        self.client.post('/api/register',
            data=json.dumps({
                'username': 'logintest',
                'email': 'login@example.com',
                'password': 'LoginPass123'
            }),
            content_type='application/json'
        )
        
        # Then login
        response = self.client.post('/api/login',
            data=json.dumps({
                'username': 'logintest',
                'password': 'LoginPass123'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('token', data['data'])
    
    def test_invalid_login(self):
        """Test invalid login credentials"""
        response = self.client.post('/api/login',
            data=json.dumps({
                'username': 'nonexistent',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()
```

Run tests:
```bash
python -m pytest test_app.py -v
```

## Integration Testing

### Database Connection Test

```python
import MySQLdb
from config import get_config

def test_database_connection():
    """Test database connection"""
    config = get_config()
    try:
        conn = MySQLdb.connect(
            host=config.DB_HOST,
            user=config.DB_USER,
            passwd=config.DB_PASSWORD,
            db=config.DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == '__main__':
    test_database_connection()
```

### Complete User Flow Test

```python
import requests
import json

BASE_URL = "http://localhost:5000"

def test_complete_flow():
    """Test complete user workflow"""
    
    print("\n=== Testing Complete User Flow ===\n")
    
    # 1. Register
    print("1. Testing Registration...")
    register_data = {
        "username": "flowtest",
        "email": "flowtest@example.com",
        "password": "FlowTest123"
    }
    resp = requests.post(f"{BASE_URL}/api/register", json=register_data)
    assert resp.status_code == 201, f"Registration failed: {resp.text}"
    user_id = resp.json()['data']['user_id']
    print("   ✓ Registration successful")
    
    # 2. Login
    print("2. Testing Login...")
    login_data = {
        "username": "flowtest",
        "password": "FlowTest123"
    }
    resp = requests.post(f"{BASE_URL}/api/login", json=login_data)
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()['data']['token']
    print("   ✓ Login successful")
    
    # 3. Create Subscription
    print("3. Testing Subscription Creation...")
    headers = {"Authorization": f"Bearer {token}"}
    subscription_data = {
        "plan_name": "Test Plan",
        "data_limit_gb": 20,
        "monthly_price": 29.99
    }
    resp = requests.post(f"{BASE_URL}/api/subscribe", json=subscription_data, headers=headers)
    assert resp.status_code == 201, f"Subscription creation failed: {resp.text}"
    subscription_id = resp.json()['data']['subscription_id']
    print("   ✓ Subscription created")
    
    # 4. Record Payment
    print("4. Testing Payment Recording...")
    payment_data = {
        "subscription_id": subscription_id,
        "amount": 29.99,
        "payment_method": "card",
        "transaction_ref": "TEST-12345"
    }
    resp = requests.post(f"{BASE_URL}/api/payment", json=payment_data, headers=headers)
    assert resp.status_code == 201, f"Payment recording failed: {resp.text}"
    print("   ✓ Payment recorded")
    
    # 5. Log Usage
    print("5. Testing Usage Logging...")
    usage_data = {
        "subscription_id": subscription_id,
        "data_used_mb": 512,
        "upload_mb": 256,
        "download_mb": 256,
        "session_duration_minutes": 60
    }
    resp = requests.post(f"{BASE_URL}/api/usage", json=usage_data, headers=headers)
    assert resp.status_code == 201, f"Usage logging failed: {resp.text}"
    print("   ✓ Usage logged")
    
    # 6. Get Dashboard Metrics
    print("6. Testing Dashboard Metrics...")
    resp = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
    assert resp.status_code == 200, f"Dashboard metrics failed: {resp.text}"
    metrics = resp.json()['data']
    print(f"   ✓ Dashboard retrieved:")
    print(f"     - Revenue: ${metrics['revenue']:.2f}")
    print(f"     - Usage: {metrics['usage_gb']:.2f} GB")
    print(f"     - Active Customers: {metrics['active_customers']}")
    
    print("\n=== All Tests Passed! ===\n")

if __name__ == '__main__':
    try:
        test_complete_flow()
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
```

Run integration test:
```bash
python integration_test.py
```

## API Testing

### Using Postman

1. **Import API Collection**
   - Create a new Postman collection
   - Add requests for each endpoint

2. **Test Scenarios**

**Register Endpoint:**
```
Method: POST
URL: http://localhost:5000/api/register
Body (JSON):
{
  "username": "postmantest",
  "email": "postman@example.com",
  "password": "PostmanTest123"
}
```

**Login Endpoint:**
```
Method: POST
URL: http://localhost:5000/api/login
Body (JSON):
{
  "username": "postmantest",
  "password": "PostmanTest123"
}
```

**Protected Endpoint:**
```
Method: GET
URL: http://localhost:5000/api/dashboard
Headers:
Authorization: Bearer <token_from_login>
```

### Using Python Requests

Create `test_api.py`:

```python
import requests

BASE_URL = "http://localhost:5000"

class TestAPI:
    def __init__(self):
        self.token = None
    
    def test_all_endpoints(self):
        self.register()
        self.login()
        self.subscribe()
        self.payment()
        self.usage()
        self.dashboard()
    
    def register(self):
        resp = requests.post(f"{BASE_URL}/api/register", json={
            "username": "apitest",
            "email": "api@test.com",
            "password": "ApiTest123"
        })
        print(f"Register: {resp.status_code}")
    
    def login(self):
        resp = requests.post(f"{BASE_URL}/api/login", json={
            "username": "apitest",
            "password": "ApiTest123"
        })
        if resp.status_code == 200:
            self.token = resp.json()['data']['token']
        print(f"Login: {resp.status_code}")
    
    def subscribe(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(f"{BASE_URL}/api/subscribe", 
            json={"plan_name": "Test", "data_limit_gb": 10, "monthly_price": 9.99},
            headers=headers)
        print(f"Subscribe: {resp.status_code}")
        return resp.json()['data']['subscription_id']
    
    def payment(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(f"{BASE_URL}/api/payment",
            json={"subscription_id": 1, "amount": 9.99, "payment_method": "card"},
            headers=headers)
        print(f"Payment: {resp.status_code}")
    
    def usage(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.post(f"{BASE_URL}/api/usage",
            json={"subscription_id": 1, "data_used_mb": 100},
            headers=headers)
        print(f"Usage: {resp.status_code}")
    
    def dashboard(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        resp = requests.get(f"{BASE_URL}/api/dashboard", headers=headers)
        print(f"Dashboard: {resp.status_code}")

if __name__ == '__main__':
    tester = TestAPI()
    tester.test_all_endpoints()
```

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
# Windows: Download from Apache website
# macOS: brew install httpd
# Linux: sudo apt-get install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 http://localhost:5000/api/health

# Test with POST data
ab -n 100 -c 5 -p data.json -T application/json http://localhost:5000/api/register
```

### Using Locust

Create `locustfile.py`:

```python
from locust import HttpUser, task, between
import json

class BillingUser(HttpUser):
    wait_time = between(1, 3)
    token = None
    
    @task
    def health_check(self):
        self.client.get("/api/health")
    
    @task
    def login(self):
        response = self.client.post("/api/login", json={
            "username": "testuser",
            "password": "TestPass123"
        })
        if response.status_code == 200:
            self.token = response.json()['data']['token']
    
    @task
    def get_dashboard(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/dashboard", headers=headers)
```

Run load test:
```bash
locust -f locustfile.py --host=http://localhost:5000
```

## Security Testing

### SQL Injection Test

```python
def test_sql_injection():
    """Test SQL injection prevention"""
    response = requests.post("http://localhost:5000/api/login", json={
        "username": "' OR '1'='1",
        "password": "' OR '1'='1"
    })
    # Should fail, not return a valid token
    assert response.status_code != 200

def test_password_hashing():
    """Verify passwords are hashed"""
    # Register user
    requests.post("http://localhost:5000/api/register", json={
        "username": "hashtest",
        "email": "hash@test.com",
        "password": "MyPassword123"
    })
    
    # Check database directly (password should be hashed)
    import MySQLdb
    conn = MySQLdb.connect(host='localhost', user='root', db='wifi_billing_system')
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = 'hashtest'")
    password_hash = cursor.fetchone()[0]
    
    # Password should not be plain text
    assert password_hash != "MyPassword123"
    # Should start with $2... (bcrypt format)
    assert password_hash.startswith('$2')
    cursor.close()
    conn.close()
```

### CORS Testing

```python
def test_cors():
    """Test CORS headers"""
    response = requests.get("http://localhost:5000/api/health")
    assert 'Access-Control-Allow-Origin' in response.headers
```

## Automated Testing

Create a comprehensive test script:

```bash
#!/bin/bash
# run_all_tests.sh

echo "Running all tests..."
echo ""

echo "1. Unit Tests"
python -m pytest test_app.py -v

echo ""
echo "2. Integration Tests"
python integration_test.py

echo ""
echo "3. API Tests"
python test_api.py

echo ""
echo "=== All Tests Complete ==="
```

Make executable and run:
```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

## Monitoring in Production

### Key Metrics to Monitor
- API response time (target: < 200ms)
- Error rate (target: < 0.1%)
- Database query time (target: < 100ms)
- Active users/connections
- Memory usage
- Disk space
- CPU usage

### Setup Monitoring

```python
# Add to app.py for metrics collection
import time
from functools import wraps

def track_metrics(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start
        print(f"[METRIC] {f.__name__} took {duration:.3f}s")
        return result
    return decorated

@app.route('/api/dashboard')
@track_metrics
@token_required
def dashboard():
    # ... endpoint code
    pass
```

---

For questions about testing, refer to the main [README.md](README.md).
