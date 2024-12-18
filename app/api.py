from flask import Flask, request
from flask_restx import Api, Resource
from config.settings import Config
from services.secrets_manager import SecretsManager
from services.login_service import LoginService
import logging
import sentry_sdk
from flasgger import Swagger


def create_app(config=None):
    """Create and configure Flask application."""
    if not config:
        config = Config()

    # Initialize Sentry for error tracking
    if config.SENTRY_DSN:
        sentry_sdk.init(dsn=config.SENTRY_DSN)

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = Flask(__name__)
    app.config.from_object(config)
    swagger = Swagger(app)

    # Initialize API
    api = Api(
        app,
        title='Secure Secret Vault',
        version='2.0',
        description='Advanced Secret Management System'
    )

    secrets_manager = SecretsManager(config)

    @api.route('/store_secret')
    class StoreSecret(Resource):
        def post(self):
            """Store a new secret securely."""
            data = request.json
            try:
                secret_id = secrets_manager.store_secret(
                    data['username'],
                    data['password']
                )
                return {'status': 'success', 'secret_id': secret_id}, 201
            except Exception as e:
                return {'status': 'error', 'message': str(e)}, 500

    @api.route('/login_tiktok')
    class TikTokLogin(Resource):
        def post(self):
            """Automated TikTok login using stored credentials."""
            data = request.json
            try:
                username, password = secrets_manager.retrieve_secret(
                    data['username'],
                    data['master_password']
                )
                login_success = LoginService.login_to_tiktok(username, password)
                return {
                    'status': 'success' if login_success else 'failed',
                    'message': 'Login attempt completed'
                }, 200
            except Exception as e:
                return {'status': 'error', 'message': str(e)}, 500

    return app
