"""
Configuration module for the Wi-Fi Billing System
Handles database connection and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'wifi_billing_system')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Database connection string for SQLAlchemy
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # API Configuration
    DEBUG = os.getenv('DEBUG', False)
    TESTING = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ALGORITHM = 'HS256'
    JWT_EXPIRATION_HOURS = 24
    
    # Password Configuration
    BCRYPT_LOG_ROUNDS = 12
    
    # Pagination
    ITEMS_PER_PAGE = 20
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', True)
    RATE_LIMIT_REQUESTS = 100  # requests
    RATE_LIMIT_PERIOD = 3600   # seconds (1 hour)
    
    # Streamlit Dashboard Configuration
    STREAMLIT_THEME = 'light'
    STREAMLIT_TITLE = 'Wi-Fi Billing System Dashboard'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

# Configuration dictionary
config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

def get_config(env=None):
    """Get the appropriate configuration class based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config_dict.get(env, DevelopmentConfig)
