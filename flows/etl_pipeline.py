from prefect import flow, task
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import Settings
from config.paths import CONFIG_DIR
from scripts.utils import get_table_structure
from scripts.extract import get_game_data, save_as_json

settings = Settings()

@task
def extract(credentials: dict) -> None:
    for key, value in get_table_structure(CONFIG_DIR).items():
        data = get_game_data(
            fields=value['fields'], 
            credentials=credentials, 
            entity_name=key
        )
        save_as_json(data=data, entity_name=key)

@flow
def main() -> None:
    extract(settings.get_igdb_connection_credentials)


if __name__ == '__main__':
    main.serve(
        name='my-first-deployment',
        cron="5 * * * *"
    )