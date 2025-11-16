from datetime import timedelta
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

class Config:
    # Database configuration for Render
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://')
    
    # Fallback to local development database
    SQLALCHEMY_DATABASE_URI = DATABASE_URL or f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration - usar variable de entorno en producción
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your_jwt_secret_key'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['cookies', 'headers']
    JWT_COOKIE_SECURE = os.environ.get('RENDER_EXTERNAL_HOSTNAME') is not None  # True en producción de Render
    JWT_COOKIE_CSRF_PROTECT = False
    JWT_ACCESS_COOKIE_NAME = 'access_token_cookie'
    JWT_REFRESH_COOKIE_NAME = 'refresh_token_cookie'
    JWT_ACCESS_COOKIE_PATH = '/'
    JWT_REFRESH_COOKIE_PATH = '/'
    JWT_COOKIE_SAMESITE = 'Lax'
    JWT_COOKIE_DOMAIN = None
    
    
    # Upload configuration for Render
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/opt/render/project/src/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

class DevelopmentConfig(Config):
    DEBUG = True
    JWT_COOKIE_SECURE = False

class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True

class RailwayConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True
    # Railway-specific settings
    UPLOAD_FOLDER = '/tmp/uploads'

#configuraciones :)
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'railway': RailwayConfig
}
