from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

def to_uppercase(name: str) -> str:
    return name.upper()

class Settings(BaseSettings):
    igdb_client_id: str
    igdb_access_token: str

    r2_account_id: str
    r2_api_token: str
    r2_access_key_id: str
    r2_secret_access_key: str

    postgres_database_host: str
    postgres_database_port: int
    postgres_database_user: str
    postgres_database_password: str
    postgres_database_name: str

    model_config = SettingsConfigDict(
        env_file = f'{Path(__file__).parent.parent}/.env',
        env_file_encoding = 'utf-8',
        extra = 'ignore'
    )
        
    @property
    def get_igdb_connection_credentials(self):
        return {
            'Client-ID': self.igdb_client_id, 
            'Authorization': f'Bearer {self.igdb_access_token}'
        }

    @property
    def get_r2_client_credentials(self, service_name: str='s3', region_name: str='auto'):
        return {
            'service_name': service_name,
            'endpoint_url': f'https://{self.r2_account_id}.r2.cloudflarestorage.com',
            'aws_access_key_id': self.r2_access_key_id,
            'aws_secret_access_key': self.r2_secret_access_key,
            'region_name': region_name,
        }

    @property
    def get_r2_secret_credentials(self):
        return f"""
            TYPE r2,
            KEY_ID '{self.r2_access_key_id}',
            SECRET '{self.r2_secret_access_key}',
            ACCOUNT_ID '{self.r2_account_id}'
        """
    
    @property
    def get_database_connection_string(self):
        host = self.postgres_database_host
        port = self.postgres_database_port
        user = self.postgres_database_user
        password = self.postgres_database_password
        dbname = self.postgres_database_name

        return f'postgresql://{user}:{password}@{host}:{port}/{dbname}'