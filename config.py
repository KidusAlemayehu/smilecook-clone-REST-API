import os


class Config:
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    SECRET_KEY = 'zQITImwb3bwq6S-rnCHzr0LeuWUuhnt230c40Z7mYo8'
    JWT_ERROR_MESSAGE = 'Error'
    Debug = False
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:3346khag@localhost/SmileCook"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 465
    MAIL_USERNAME = "kidusalemayehu705@gmail.com"
    MAIL_PASSWORD = "3346khag"
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_DEFAULT_SENDER = "kidusalemayehu705@gmail.com"
    UPLOADED_IMAGES_DEST = 'static/images'
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 10*60*60
    RATELIMIT_HEADERS_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'zQITImwb3bwq6S-rnCHzr0LeuWUuhnt230c40Z7mYo8'
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:3346khag@localhost/SmileCook"
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1)


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    MAIL_SERVER = os.environ.get('EMAIL_SERVER')
    MAIL_PORT = os.environ.get('EMAIL_PORT')
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEFAULT_SENDER = os.environ.get('EMAIL_DEFAULT_SENDER')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1)


class StagingConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1)
