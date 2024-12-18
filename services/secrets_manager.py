import boto3
import logging
import json
import base64
from botocore.exceptions import ClientError
from security.encryption import SecureEncryption


class SecretsManager:
    """Advanced secrets management with AWS integration."""

    def __init__(self, config):
        self.config = config
        self.client = boto3.client(
            'secretsmanager',
            region_name=config.AWS_REGION
        )
        self.logger = logging.getLogger(__name__)

    def store_secret(self, username: str, password: str):
        """Securely store a secret with advanced encryption."""
        try:
            # Generate a unique encryption key
            key, salt = SecureEncryption.generate_key(password)

            # Encrypt the entire payload
            encrypted_payload = {
                'username': SecureEncryption.encrypt(username, key),
                'password': SecureEncryption.encrypt(password, key),
                'salt': base64.b64encode(salt).decode()
            }

            secret_id = f"vault-secret-{username}"
            self.client.create_secret(
                Name=secret_id,
                SecretString=json.dumps(encrypted_payload)
            )
            return secret_id

        except ClientError as e:
            self.logger.error(f"Secret storage failed: {e}")
            raise

    def retrieve_secret(self, username: str, master_password: str):
        """Retrieve and decrypt a stored secret."""
        try:
            secret_id = f"vault-secret-{username}"
            response = self.client.get_secret_value(SecretId=secret_id)

            payload = json.loads(response['SecretString'])
            salt = base64.b64decode(payload['salt'])

            # Regenerate the key using the stored salt
            key, _ = SecureEncryption.generate_key(master_password, salt)

            decrypted_username = SecureEncryption.decrypt(payload['username'], key)
            decrypted_password = SecureEncryption.decrypt(payload['password'], key)

            return decrypted_username, decrypted_password

        except ClientError as e:
            self.logger.error(f"Secret retrieval failed: {e}")
            raise
