import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DB = os.getenv('MYSQL_DB', 'sklad_db')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', '3306'))
    
    # Flask configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # MySQL settings
    MYSQL_UNIX_SOCKET = None
    MYSQL_CONNECT_TIMEOUT = 10
    MYSQL_READ_DEFAULT_FILE = None
    MYSQL_USE_UNICODE = True
    MYSQL_CHARSET = 'utf8'
    MYSQL_SQL_MODE = None
    MYSQL_CURSORCLASS = 'DictCursor'