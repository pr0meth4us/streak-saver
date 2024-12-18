import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    AWS_REGION = 'ap-southeast-1'
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = 3600
    INTEGRITY_CHECK_INTERVAL = 300
    FLASK_ENV = os.getenv('FLASK_ENV')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    SENTRY_DSN = os.getenv('SENTRY_DSN')
    DEBUG = FLASK_ENV == 'development'
