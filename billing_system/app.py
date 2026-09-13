"""
Flask Backend Application for Wi-Fi Billing System
Provides REST API endpoints for user management, subscriptions, payments, and usage tracking
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from flask_mysqldb import MySQL
import MySQLdb.cursors
import bcrypt
import jwt
import datetime
import json
from functools import wraps
from decimal import Decimal
from config import get_config
import os

# Initialize Flask app
app = Flask(__name__)

# Load configuration
config = get_config(os.getenv('FLASK_ENV', 'development'))
app.config.from_object(config)

# Initialize extensions
CORS(app, resources={r"/api/*": {"origins": "*"}})
mysql = MySQL(app)

# ===================== HELPER FUNCTIONS =====================

def decimal_to_float(obj):
    """Convert Decimal objects to float for JSON serialization"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def generate_jwt_token(user_id, username):
    """Generate JWT token for authenticated user"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=config.JWT_EXPIRATION_HOURS),
        'iat': datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm=config.JWT_ALGORITHM)
    return token

def verify_jwt_token(token):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=[config.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require JWT token for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'success': False, 'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'success': False, 'message': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        request.username = payload['username']
        
        return f(*args, **kwargs)
    
    return decorated

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=config.BCRYPT_LOG_ROUNDS)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# ===================== AUTHENTICATION ENDPOINTS =====================

@app.route('/api/register', methods=['POST'])
def register():
    """
    Register a new user
    POST /api/register
    Body: {
        "username": "string",
        "email": "string",
        "password": "string",
        "phone_number": "string" (optional)
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        username = data['username']
        email = data['email']
        password = data['password']
        phone_number = data.get('phone_number', '')
        
        # Validate email format
        if '@' not in email:
            return jsonify({'success': False, 'message': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Insert into database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, phone_number, status) VALUES (%s, %s, %s, %s, %s)",
                (username, email, password_hash, phone_number, 'active')
            )
            mysql.connection.commit()
            
            user_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': 'User registered successfully',
                'data': {
                    'user_id': user_id,
                    'username': username,
                    'email': email
                }
            }), 201
        
        except MySQLdb.IntegrityError:
            mysql.connection.rollback()
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 409
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Registration failed: {str(e)}'}), 500
    finally:
        cursor.close()

@app.route('/api/login', methods=['POST'])
def login():
    """
    Authenticate user and return JWT token
    POST /api/login
    Body: {
        "username": "string",
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'success': False, 'message': 'Missing username or password'}), 400
        
        username = data['username']
        password = data['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT user_id, username, email, password_hash, status FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        if user['status'] != 'active':
            return jsonify({'success': False, 'message': 'Account is not active'}), 403
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return jsonify({'success': False, 'message': 'Invalid username or password'}), 401
        
        # Generate JWT token
        token = generate_jwt_token(user['user_id'], user['username'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'token': token
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Login failed: {str(e)}'}), 500

# ===================== SUBSCRIPTION ENDPOINTS =====================

@app.route('/api/subscribe', methods=['POST'])
@token_required
def subscribe():
    """
    Create a new subscription for authenticated user
    POST /api/subscribe
    Headers: Authorization: Bearer <token>
    Body: {
        "plan_name": "string",
        "data_limit_gb": "number",
        "monthly_price": "number"
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['plan_name', 'data_limit_gb', 'monthly_price']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        user_id = request.user_id
        plan_name = data['plan_name']
        data_limit_gb = float(data['data_limit_gb'])
        monthly_price = float(data['monthly_price'])
        
        # Validate input
        if data_limit_gb <= 0 or monthly_price <= 0:
            return jsonify({'success': False, 'message': 'Data limit and price must be positive'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Set subscription dates
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)
        renewal_date = end_date
        
        try:
            cursor.execute(
                """INSERT INTO subscriptions 
                (user_id, plan_name, data_limit_gb, monthly_price, status, start_date, end_date, renewal_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (user_id, plan_name, data_limit_gb, monthly_price, 'active', start_date, end_date, renewal_date)
            )
            mysql.connection.commit()
            
            subscription_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': 'Subscription created successfully',
                'data': {
                    'subscription_id': subscription_id,
                    'user_id': user_id,
                    'plan_name': plan_name,
                    'data_limit_gb': data_limit_gb,
                    'monthly_price': monthly_price,
                    'status': 'active',
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                }
            }), 201
        
        except Exception as e:
            mysql.connection.rollback()
            raise e
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Subscription creation failed: {str(e)}'}), 500
    finally:
        cursor.close()

# ===================== PAYMENT ENDPOINTS =====================

@app.route('/api/payment', methods=['POST'])
@token_required
def record_payment():
    """
    Record a payment for a subscription
    POST /api/payment
    Headers: Authorization: Bearer <token>
    Body: {
        "subscription_id": "integer",
        "amount": "number",
        "payment_method": "string" (e.g., 'mpesa', 'card', 'bank'),
        "transaction_ref": "string" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['subscription_id', 'amount', 'payment_method']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        subscription_id = int(data['subscription_id'])
        amount = float(data['amount'])
        payment_method = data['payment_method']
        transaction_ref = data.get('transaction_ref', f'TXN-{datetime.datetime.now().timestamp()}')
        
        # Validate amount
        if amount <= 0:
            return jsonify({'success': False, 'message': 'Amount must be positive'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Verify subscription belongs to current user
        cursor.execute("SELECT user_id, status FROM subscriptions WHERE subscription_id = %s", (subscription_id,))
        subscription = cursor.fetchone()
        
        if not subscription:
            cursor.close()
            return jsonify({'success': False, 'message': 'Subscription not found'}), 404
        
        if subscription['user_id'] != request.user_id:
            cursor.close()
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            # Record payment
            cursor.execute(
                """INSERT INTO payments 
                (subscription_id, amount, payment_method, transaction_ref, status) 
                VALUES (%s, %s, %s, %s, %s)""",
                (subscription_id, amount, payment_method, transaction_ref, 'success')
            )
            mysql.connection.commit()
            
            payment_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': 'Payment recorded successfully',
                'data': {
                    'payment_id': payment_id,
                    'subscription_id': subscription_id,
                    'amount': amount,
                    'payment_method': payment_method,
                    'transaction_ref': transaction_ref,
                    'status': 'success',
                    'payment_date': datetime.datetime.now().isoformat()
                }
            }), 201
        
        except Exception as e:
            mysql.connection.rollback()
            raise e
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Payment recording failed: {str(e)}'}), 500
    finally:
        cursor.close()

# ===================== USAGE ENDPOINTS =====================

@app.route('/api/usage', methods=['POST'])
@token_required
def log_usage():
    """
    Log data usage for a subscription
    POST /api/usage
    Headers: Authorization: Bearer <token>
    Body: {
        "subscription_id": "integer",
        "data_used_mb": "number",
        "upload_mb": "number" (optional),
        "download_mb": "number" (optional),
        "session_duration_minutes": "integer" (optional)
    }
    """
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ['subscription_id', 'data_used_mb']):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        subscription_id = int(data['subscription_id'])
        data_used_mb = float(data['data_used_mb'])
        upload_mb = float(data.get('upload_mb', 0))
        download_mb = float(data.get('download_mb', 0))
        session_duration_minutes = int(data.get('session_duration_minutes', 0))
        
        # Validate data
        if data_used_mb < 0:
            return jsonify({'success': False, 'message': 'Data usage must be non-negative'}), 400
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Verify subscription belongs to current user
        cursor.execute("SELECT user_id FROM subscriptions WHERE subscription_id = %s", (subscription_id,))
        subscription = cursor.fetchone()
        
        if not subscription:
            cursor.close()
            return jsonify({'success': False, 'message': 'Subscription not found'}), 404
        
        if subscription['user_id'] != request.user_id:
            cursor.close()
            return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
        try:
            # Log usage
            cursor.execute(
                """INSERT INTO usage_logs 
                (subscription_id, data_used_mb, upload_mb, download_mb, session_duration_minutes) 
                VALUES (%s, %s, %s, %s, %s)""",
                (subscription_id, data_used_mb, upload_mb, download_mb, session_duration_minutes)
            )
            mysql.connection.commit()
            
            usage_id = cursor.lastrowid
            
            return jsonify({
                'success': True,
                'message': 'Usage logged successfully',
                'data': {
                    'usage_id': usage_id,
                    'subscription_id': subscription_id,
                    'data_used_mb': data_used_mb,
                    'upload_mb': upload_mb,
                    'download_mb': download_mb,
                    'session_duration_minutes': session_duration_minutes
                }
            }), 201
        
        except Exception as e:
            mysql.connection.rollback()
            raise e
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Usage logging failed: {str(e)}'}), 500
    finally:
        cursor.close()

# ===================== DASHBOARD ENDPOINTS =====================

@app.route('/api/dashboard', methods=['GET'])
@token_required
def dashboard():
    """
    Return monthly metrics for the dashboard
    GET /api/dashboard
    Headers: Authorization: Bearer <token>
    Returns: {
        "revenue": number,
        "usage": number,
        "active_customers": integer,
        "churned_customers": integer
    }
    """
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Get current month date range
        today = datetime.date.today()
        month_start = today.replace(day=1)
        if today.month == 12:
            month_end = month_start.replace(year=today.year + 1, month=1) - datetime.timedelta(days=1)
        else:
            month_end = month_start.replace(month=today.month + 1) - datetime.timedelta(days=1)
        
        # Monthly Revenue (SUM of successful payments)
        cursor.execute(
            """SELECT COALESCE(SUM(amount), 0) as total_revenue 
            FROM payments 
            WHERE status = 'success' AND DATE(payment_date) BETWEEN %s AND %s""",
            (month_start, month_end)
        )
        revenue_result = cursor.fetchone()
        total_revenue = float(revenue_result['total_revenue']) if revenue_result else 0
        
        # Monthly Data Usage (SUM of usage_logs)
        cursor.execute(
            """SELECT COALESCE(SUM(data_used_mb), 0) as total_usage 
            FROM usage_logs 
            WHERE DATE(log_date) BETWEEN %s AND %s""",
            (month_start, month_end)
        )
        usage_result = cursor.fetchone()
        total_usage_mb = float(usage_result['total_usage']) if usage_result else 0
        
        # Active Customers (subscriptions with status = active)
        cursor.execute(
            """SELECT COUNT(DISTINCT user_id) as active_count 
            FROM subscriptions 
            WHERE status = 'active'"""
        )
        active_result = cursor.fetchone()
        active_customers = int(active_result['active_count']) if active_result else 0
        
        # Churned Customers (subscriptions with status = expired or cancelled)
        cursor.execute(
            """SELECT COUNT(DISTINCT user_id) as churned_count 
            FROM subscriptions 
            WHERE status IN ('expired', 'cancelled')"""
        )
        churned_result = cursor.fetchone()
        churned_customers = int(churned_result['churned_count']) if churned_result else 0
        
        cursor.close()
        
        return jsonify({
            'success': True,
            'data': {
                'period': f'{month_start} to {month_end}',
                'revenue': total_revenue,
                'usage_mb': total_usage_mb,
                'usage_gb': total_usage_mb / 1024,
                'active_customers': active_customers,
                'churned_customers': churned_customers,
                'total_customers': active_customers + churned_customers
            }
        }), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Dashboard query failed: {str(e)}'}), 500

# ===================== HEALTH CHECK =====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}), 500

# ===================== FRONTEND ROUTES =====================

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/register')
def register_page():
    """Serve registration page"""
    return render_template('register.html')

@app.route('/login')
def login_page():
    """Serve login page"""
    return render_template('login.html')

@app.route('/dashboard')
@token_required
def dashboard_page():
    """Serve dashboard page"""
    return render_template('dashboard.html')

# ===================== ERROR HANDLERS =====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ===================== MAIN =====================

if __name__ == '__main__':
    app.run(
        host=os.getenv('FLASK_HOST', '0.0.0.0'),
        port=int(os.getenv('FLASK_PORT', 5000)),
        debug=config.DEBUG
    )
