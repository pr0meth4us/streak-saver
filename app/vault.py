import hashlib
import json
import logging
import time

import boto3
from cryptography.fernet import Fernet


class TamperResistantVault:
    def __init__(self, config):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.config = config
        try:
            self.secrets_manager = boto3.client(
                'secretsmanager',
                region_name=config.AWS_REGION,
                aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
            )
        except Exception as e:
            self.logger.error(f"Failed to initialize AWS Secrets Manager: {e}")
            raise

        self.encryption_key = Fernet.generate_key()
        self.fernet = Fernet(self.encryption_key)
        self._initial_code_hash = self._get_code_hash()
        self._last_integrity_check = time.time()

    def _get_code_hash(self):
        """Generate a cryptographic hash of the current code."""
        try:
            with open(__file__, 'rb') as f:
                return hashlib.sha512(f.read()).hexdigest()
        except Exception as e:
            self.logger.error(f"Code hash generation failed: {e}")
            return None

    def _verify_code_integrity(self):
        """More lenient code integrity check."""
        # Only perform check in non-development environments
        if hasattr(self.config, 'FLASK_ENV') and self.config.FLASK_ENV != 'development':
            try:
                current_time = time.time()
                if current_time - self._last_integrity_check > self.config.INTEGRITY_CHECK_INTERVAL:
                    current_code_hash = self._get_code_hash()
                    if current_code_hash and current_code_hash != self._initial_code_hash:
                        self.logger.warning("Potential code tampering detected!")
                        # Log and alert instead of immediate self-destruct
                        # You might want to implement a more sophisticated alert mechanism
                    self._last_integrity_check = current_time
            except Exception as e:
                self.logger.error(f"Integrity check failed: {e}")

    def store_secret(self, username, password):
        self._verify_code_integrity()

        try:
            encrypted_data = self.fernet.encrypt(json.dumps({
                'username': username,
                'password': password
            }).encode())

            secret_id = f"secret-{username}"
            self.secrets_manager.create_secret(
                Name=secret_id,
                SecretString=json.dumps({'encrypted_data': encrypted_data.decode()})
            )
            return secret_id
        except Exception as e:
            self.logger.error(f"Secret storage failed: {e}")
            raise

    def use_secrets_for_task(self, username, task_function):
        print(username, task_function)

        secret_id = f"secret-{username}"
        secret_value = self.secrets_manager.get_secret_value(SecretId=secret_id)
        print(secret_value)
        encrypted_data = json.loads(secret_value['SecretString'])['encrypted_data']
        print(encrypted_data)
        decrypted_data = json.loads(self.fernet.decrypt(encrypted_data.encode()).decode())

        credential = decrypted_data['username']
        if "@" in credential:
            credential_type = "email"
        elif credential.isdigit():  # Likely a phone number
            credential_type = "phone"
        else:
            credential_type = "username"

        task_function(credential, decrypted_data['password'], credential_type)
