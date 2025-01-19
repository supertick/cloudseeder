from typing import Dict
import boto3
from botocore.exceptions import BotoCoreError, ClientError
from .interface import AuthProvider
from typing import Optional

class CognitoAuthProvider(AuthProvider):
    """AWS Cognito authentication provider."""


    def __init__(self, config: Dict[str, str]):
        self.client = boto3.client("cognito-idp")
        self.config = config
        self.user_pool_id = config.get("user_pool_id")
        self.client_id = config.get("client_id")

    def register_user(self, username: str, password: str) -> dict:
        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": username}]
            )
            return response
        except (BotoCoreError, ClientError) as e:
            raise RuntimeError(f"Registration failed: {e}")

    def authenticate(self, username: str, password: str) -> Optional[str]:
        try:
            response = self.client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
                ClientId=self.client_id
            )
            return response.get("AuthenticationResult", {}).get("IdToken")
        except (BotoCoreError, ClientError) as e:
            return None

    def get_user(self, token: str) -> Optional[dict]:
        try:
            response = self.client.get_user(AccessToken=token)
            return response.get("UserAttributes")
        except (BotoCoreError, ClientError) as e:
            return None

    def refresh_token(self, refresh_token: str) -> Optional[str]:
        try:
            response = self.client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token},
                ClientId=self.client_id
            )
            return response.get("AuthenticationResult", {}).get("IdToken")
        except (BotoCoreError, ClientError) as e:
            return None

    def logout(self, token: str) -> bool:
        try:
            self.client.global_sign_out(AccessToken=token)
            return True
        except (BotoCoreError, ClientError) as e:
            return False
