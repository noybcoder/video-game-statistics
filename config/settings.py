from pydantic_settings import BaseSettings, SettingsConfigDict

def to_uppercase(name: str) -> str:
    return name.upper()

class Settings(BaseSettings):
    igdb_client_id: str
    igdb_access_token: str

    postgres_database_host: str
    postgres_database_port: int
    postgres_database_user: str
    postgres_database_password: str
    postgres_database_name: str

    model_config = SettingsConfigDict(
        env_file = '.env',
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
    def get_schema_creation_database_credentials(self):
        return {
            'host': self.postgres_database_host,
            'port': self.postgres_database_port,
            'user': self.postgres_database_user,
            'password': self.postgres_database_password,
            'dbname': self.postgres_database_name
        }

    @property
    def get_data_load_database_credentials(self):
        credentials = self.get_schema_creation_database_credentials
        return ' '.join([f'{k}={v}' for k, v in credentials.items()])