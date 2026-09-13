-- Wi-Fi Billing System Database Schema

CREATE DATABASE IF NOT EXISTS wifi_billing_system;
USE wifi_billing_system;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username)
);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    data_limit_gb DECIMAL(10, 2) NOT NULL,
    monthly_price DECIMAL(10, 2) NOT NULL,
    status ENUM('active', 'inactive', 'expired', 'cancelled') DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE,
    renewal_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status)
);

-- Payments Table
CREATE TABLE IF NOT EXISTS payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_ref VARCHAR(100),
    status ENUM('success', 'failed', 'pending', 'refunded') DEFAULT 'pending',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    INDEX idx_subscription_id (subscription_id),
    INDEX idx_status (status),
    INDEX idx_payment_date (payment_date)
);

-- Usage Logs Table
CREATE TABLE IF NOT EXISTS usage_logs (
    usage_id INT AUTO_INCREMENT PRIMARY KEY,
    subscription_id INT NOT NULL,
    data_used_mb DECIMAL(15, 2) NOT NULL,
    upload_mb DECIMAL(15, 2) DEFAULT 0,
    download_mb DECIMAL(15, 2) DEFAULT 0,
    session_duration_minutes INT,
    log_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(subscription_id) ON DELETE CASCADE,
    INDEX idx_subscription_id (subscription_id),
    INDEX idx_log_date (log_date)
);

-- Indexes for performance
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_subscriptions_created_at ON subscriptions(created_at);
CREATE INDEX idx_payments_payment_date ON payments(payment_date);
CREATE INDEX idx_usage_logs_log_date ON usage_logs(log_date);
