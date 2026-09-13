"""
Streamlit Dashboard for Wi-Fi Billing System
Provides real-time visualization of billing metrics, revenue, usage, and customer analytics
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Streamlit page configuration
st.set_page_config(
    page_title="Wi-Fi Billing System Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling
st.markdown("""
    <style>
        .metric-card {
            padding: 20px;
            border-radius: 10px;
            background-color: #f0f2f6;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .header {
            color: #1f77b4;
            font-size: 2.5rem;
            font-weight: bold;
            margin-bottom: 30px;
        }
    </style>
""", unsafe_allow_html=True)

# ===================== DATABASE CONNECTION =====================

@st.cache_resource
def get_db_connection():
    """Create and cache database connection"""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'wifi_billing_system'),
            port=int(os.getenv('DB_PORT', 3306))
        )
        return connection
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def execute_query(connection, query, params=None):
    """Execute a database query and return results as DataFrame"""
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return pd.DataFrame(result)
    except Error as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# ===================== SIDEBAR FILTERS =====================

st.sidebar.title("⚙️ Dashboard Filters")

# Date range selector
date_range = st.sidebar.selectbox(
    "Select Time Period",
    ["Today", "This Week", "This Month", "Last Month", "Last 3 Months", "Custom"]
)

# Calculate date range
today = datetime.now().date()
if date_range == "Today":
    start_date = today
    end_date = today
elif date_range == "This Week":
    start_date = today - timedelta(days=today.weekday())
    end_date = today
elif date_range == "This Month":
    start_date = today.replace(day=1)
    end_date = today
elif date_range == "Last Month":
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    start_date = last_day_last_month.replace(day=1)
    end_date = last_day_last_month
elif date_range == "Last 3 Months":
    start_date = today - timedelta(days=90)
    end_date = today
else:
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", today - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", today)

# Status filter
status_filter = st.sidebar.multiselect(
    "Filter by Subscription Status",
    ["active", "inactive", "expired", "cancelled"],
    default=["active"]
)

# ===================== MAIN DASHBOARD =====================

st.markdown("<div class='header'>📊 Wi-Fi Billing System Dashboard</div>", unsafe_allow_html=True)
st.markdown(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Get database connection
conn = get_db_connection()

if conn:
    # ===================== KEY METRICS =====================
    
    st.markdown("## 📈 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Total Revenue
        revenue_query = """
        SELECT COALESCE(SUM(amount), 0) as total_revenue 
        FROM payments 
        WHERE status = 'success' AND DATE(payment_date) BETWEEN %s AND %s
        """
        revenue_df = execute_query(conn, revenue_query, (start_date, end_date))
        total_revenue = revenue_df['total_revenue'].values[0] if not revenue_df.empty else 0
        st.metric("💰 Total Revenue", f"${total_revenue:,.2f}")
    
    with col2:
        # Data Usage
        usage_query = """
        SELECT COALESCE(SUM(data_used_mb), 0) as total_usage 
        FROM usage_logs 
        WHERE DATE(log_date) BETWEEN %s AND %s
        """
        usage_df = execute_query(conn, usage_query, (start_date, end_date))
        total_usage_mb = usage_df['total_usage'].values[0] if not usage_df.empty else 0
        total_usage_gb = total_usage_mb / 1024
        st.metric("📊 Data Usage", f"{total_usage_gb:,.2f} GB")
    
    with col3:
        # Active Customers
        active_query = """
        SELECT COUNT(DISTINCT user_id) as active_count 
        FROM subscriptions 
        WHERE status IN %s
        """
        active_df = execute_query(conn, active_query, (tuple(status_filter),))
        active_customers = active_df['active_count'].values[0] if not active_df.empty else 0
        st.metric("👥 Active Customers", active_customers)
    
    with col4:
        # Churned Customers
        churned_query = """
        SELECT COUNT(DISTINCT user_id) as churned_count 
        FROM subscriptions 
        WHERE status IN ('expired', 'cancelled')
        """
        churned_df = execute_query(conn, churned_query)
        churned_customers = churned_df['churned_count'].values[0] if not churned_df.empty else 0
        st.metric("📉 Churned Customers", churned_customers)
    
    st.markdown("---")
    
    # ===================== REVENUE ANALYTICS =====================
    
    st.markdown("## 💹 Revenue Analytics")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Daily Revenue Trend
        daily_revenue_query = """
        SELECT DATE(payment_date) as date, SUM(amount) as revenue
        FROM payments 
        WHERE status = 'success' AND DATE(payment_date) BETWEEN %s AND %s
        GROUP BY DATE(payment_date)
        ORDER BY date
        """
        daily_revenue_df = execute_query(conn, daily_revenue_query, (start_date, end_date))
        
        if not daily_revenue_df.empty:
            fig_revenue = px.line(
                daily_revenue_df,
                x='date',
                y='revenue',
                title='Daily Revenue Trend',
                labels={'revenue': 'Revenue ($)', 'date': 'Date'},
                markers=True
            )
            fig_revenue.update_layout(hovermode='x unified')
            st.plotly_chart(fig_revenue, use_container_width=True)
        else:
            st.info("No revenue data available for the selected period")
    
    with col2:
        # Revenue by Payment Method
        payment_method_query = """
        SELECT payment_method, COUNT(*) as count, SUM(amount) as total
        FROM payments 
        WHERE status = 'success' AND DATE(payment_date) BETWEEN %s AND %s
        GROUP BY payment_method
        """
        payment_method_df = execute_query(conn, payment_method_query, (start_date, end_date))
        
        if not payment_method_df.empty:
            fig_payment = px.pie(
                payment_method_df,
                values='total',
                names='payment_method',
                title='Revenue by Payment Method'
            )
            st.plotly_chart(fig_payment, use_container_width=True)
        else:
            st.info("No payment method data available")
    
    st.markdown("---")
    
    # ===================== USAGE ANALYTICS =====================
    
    st.markdown("## 📊 Usage Analytics")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Daily Data Usage Trend
        daily_usage_query = """
        SELECT DATE(log_date) as date, SUM(data_used_mb) as usage_mb
        FROM usage_logs 
        WHERE DATE(log_date) BETWEEN %s AND %s
        GROUP BY DATE(log_date)
        ORDER BY date
        """
        daily_usage_df = execute_query(conn, daily_usage_query, (start_date, end_date))
        
        if not daily_usage_df.empty:
            daily_usage_df['usage_gb'] = daily_usage_df['usage_mb'] / 1024
            fig_usage = px.bar(
                daily_usage_df,
                x='date',
                y='usage_gb',
                title='Daily Data Usage Trend',
                labels={'usage_gb': 'Usage (GB)', 'date': 'Date'}
            )
            st.plotly_chart(fig_usage, use_container_width=True)
        else:
            st.info("No usage data available for the selected period")
    
    with col2:
        # Top Data Consumers
        top_users_query = """
        SELECT u.username, SUM(ul.data_used_mb) as total_usage_mb
        FROM usage_logs ul
        JOIN subscriptions s ON ul.subscription_id = s.subscription_id
        JOIN users u ON s.user_id = u.user_id
        WHERE DATE(ul.log_date) BETWEEN %s AND %s
        GROUP BY u.user_id
        ORDER BY total_usage_mb DESC
        LIMIT 10
        """
        top_users_df = execute_query(conn, top_users_query, (start_date, end_date))
        
        if not top_users_df.empty:
            top_users_df['total_usage_gb'] = top_users_df['total_usage_mb'] / 1024
            fig_top = px.bar(
                top_users_df,
                x='total_usage_gb',
                y='username',
                orientation='h',
                title='Top 10 Data Consumers',
                labels={'total_usage_gb': 'Usage (GB)'}
            )
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.info("No user data available")
    
    st.markdown("---")
    
    # ===================== CUSTOMER ANALYTICS =====================
    
    st.markdown("## 👥 Customer Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Subscription Status Distribution
        status_query = """
        SELECT status, COUNT(*) as count
        FROM subscriptions 
        GROUP BY status
        """
        status_df = execute_query(conn, status_query)
        
        if not status_df.empty:
            fig_status = px.pie(
                status_df,
                values='count',
                names='status',
                title='Subscription Status Distribution'
            )
            st.plotly_chart(fig_status, use_container_width=True)
        else:
            st.info("No subscription data available")
    
    with col2:
        # Plan Distribution
        plan_query = """
        SELECT plan_name, COUNT(*) as count, ROUND(AVG(data_limit_gb), 2) as avg_data
        FROM subscriptions 
        WHERE status IN %s
        GROUP BY plan_name
        """
        plan_df = execute_query(conn, plan_query, (tuple(status_filter),))
        
        if not plan_df.empty:
            fig_plan = px.bar(
                plan_df,
                x='plan_name',
                y='count',
                title='Active Customers by Plan',
                labels={'count': 'Number of Customers', 'plan_name': 'Plan'}
            )
            st.plotly_chart(fig_plan, use_container_width=True)
        else:
            st.info("No plan data available")
    
    st.markdown("---")
    
    # ===================== DETAILED TABLES =====================
    
    st.markdown("## 📋 Detailed Data")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Payments", "Usage", "Subscriptions", "Users"])
    
    with tab1:
        st.subheader("Recent Payments")
        payments_query = """
        SELECT p.payment_id, u.username, s.plan_name, p.amount, p.payment_method, p.status, p.payment_date
        FROM payments p
        JOIN subscriptions s ON p.subscription_id = s.subscription_id
        JOIN users u ON s.user_id = u.user_id
        WHERE DATE(p.payment_date) BETWEEN %s AND %s
        ORDER BY p.payment_date DESC
        LIMIT 100
        """
        payments_df = execute_query(conn, payments_query, (start_date, end_date))
        
        if not payments_df.empty:
            st.dataframe(payments_df, use_container_width=True)
            st.write(f"**Total Records:** {len(payments_df)}")
        else:
            st.info("No payment records available")
    
    with tab2:
        st.subheader("Usage Logs")
        usage_query = """
        SELECT ul.usage_id, u.username, s.plan_name, ul.data_used_mb, ul.upload_mb, ul.download_mb, ul.log_date
        FROM usage_logs ul
        JOIN subscriptions s ON ul.subscription_id = s.subscription_id
        JOIN users u ON s.user_id = u.user_id
        WHERE DATE(ul.log_date) BETWEEN %s AND %s
        ORDER BY ul.log_date DESC
        LIMIT 100
        """
        usage_df = execute_query(conn, usage_query, (start_date, end_date))
        
        if not usage_df.empty:
            st.dataframe(usage_df, use_container_width=True)
            st.write(f"**Total Records:** {len(usage_df)}")
        else:
            st.info("No usage records available")
    
    with tab3:
        st.subheader("Subscriptions")
        subscriptions_query = """
        SELECT s.subscription_id, u.username, s.plan_name, s.data_limit_gb, s.monthly_price, s.status, s.start_date, s.end_date
        FROM subscriptions s
        JOIN users u ON s.user_id = u.user_id
        WHERE s.status IN %s
        ORDER BY s.created_at DESC
        LIMIT 100
        """
        subscriptions_df = execute_query(conn, subscriptions_query, (tuple(status_filter),))
        
        if not subscriptions_df.empty:
            st.dataframe(subscriptions_df, use_container_width=True)
            st.write(f"**Total Records:** {len(subscriptions_df)}")
        else:
            st.info("No subscription records available")
    
    with tab4:
        st.subheader("Users")
        users_query = """
        SELECT user_id, username, email, phone_number, status, created_at
        FROM users
        ORDER BY created_at DESC
        LIMIT 100
        """
        users_df = execute_query(conn, users_query)
        
        if not users_df.empty:
            st.dataframe(users_df, use_container_width=True)
            st.write(f"**Total Records:** {len(users_df)}")
        else:
            st.info("No user records available")
    
    # Close connection
    conn.close()

else:
    st.error("Unable to connect to the database. Please check your configuration.")
    st.stop()

# ===================== FOOTER =====================

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: gray; padding: 20px;'>
        <p>Wi-Fi Billing System Dashboard | Last updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
""", unsafe_allow_html=True)
