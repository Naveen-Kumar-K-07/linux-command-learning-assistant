import os
import socket
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def get_database_uri():
    # Allow explicit override via DATABASE_URL
    explicit_url = os.environ.get('DATABASE_URL')
    if explicit_url:
        return explicit_url
        
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = int(os.environ.get('MYSQL_PORT', 3306))
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_pass = os.environ.get('MYSQL_PASSWORD', 'root')
    mysql_db = os.environ.get('MYSQL_DB', 'linux_learning_assistant')

    # Check if MySQL port is open and responding
    mysql_available = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((mysql_host, mysql_port))
        sock.close()
        if result == 0:
            mysql_available = True
    except Exception:
        mysql_available = False
        
    if mysql_available:
        return f"mysql+pymysql://{mysql_user}:{mysql_pass}@{mysql_host}:{mysql_port}/{mysql_db}?charset=utf8mb4"
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, 'database', 'linux_learning.db')
        return f"sqlite:///{db_path}"

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-linux-assistant-key-2026'
    
    # Session security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Mail settings for Gmail verification
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() in ('true', '1', 't')
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@linuxassistant.local')
    
    # Dev mode helper to show verification code on UI or auto-verify
    DEV_MODE_AUTO_VERIFY = os.environ.get('DEV_MODE_AUTO_VERIFY', 'True').lower() in ('true', '1', 't')
    
    # Database configuration
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT', 3306))
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'root')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'linux_learning_assistant')
    
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
