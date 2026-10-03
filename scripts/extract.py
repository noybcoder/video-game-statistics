from requests import post
from datetime import datetime
from requests.exceptions import HTTPError, JSONDecodeError
import json, time, os, sys, io, boto3

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.utils import get_table_structure, get_timestamp
from config.settings import Settings
from config.paths import CONFIG_DIR, BRONZE_DIR
from config.storage import connect_to_r2_using_boto3, serialize_json_data, upload_object_to_r2_bucket, create_r2_bucket

def get_query(last_id: int, fields: list, limit: int=500, entity_name: str='games', year: int=2011, month: int=1, day: int=1):
    filter_condition = [f'id > {last_id}']

    if entity_name == 'games':
        filter_condition.append(f'first_release_date >= {int(get_timestamp(year, month, day))}')

    return f"""
        fields {', '.join(fields)};
        sort id asc;
        where {' & '.join(filter_condition)};
        limit {limit};
    """

def get_game_data(fields: list, igdb_credentials: dict, limit: int=500, entity_name: str='games', year: int=2011, month: int=1, day: int=1) -> list:
    master_responses = []
    last_id = 0

    while True:
        query = get_query(last_id, fields, limit, entity_name, year, month, day)

        try:
            response = post(
                f'https://api.igdb.com/v4/{entity_name}', 
                **{'headers': igdb_credentials, 'data': query})
            response.raise_for_status()
        except HTTPError as err:
            print(err)
            return master_responses

        try:
            game_data = response.json()
        except JSONDecodeError as err:
            print(err)
            return master_responses

        if not game_data:
            print("No more response.")
            break

        last_id = game_data[-1]['id']

        print ("response: %s" % str(game_data))
        master_responses.extend(game_data)
        time.sleep(0.25)

    return master_responses

def get_file_name(entity_name: str, output_folder: str) -> str:
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f'{output_folder}/{entity_name}_raw_{timestamp}.json'

def get_output_data(data, entity_name: str) -> dict:
    return {
        'metadata': {
            'entity': entity_name,
            'extracted_at': datetime.now().isoformat(),
            'record_count': len(data),
            'source': 'IGDB API',
            'version': 'v4'
        },
        'data': data
    }

def save_as_json(s3, bucket, data, content_type, entity_name: str, output_folder: str) -> str:
    filename = get_file_name(entity_name, output_folder)
    data = get_output_data(data, entity_name)

    if not data['data']:
        print(f'No data retrieved for "{entity_name}"')
        return None

    serialized_data = serialize_json_data(data)
    upload_object_to_r2_bucket(s3, bucket, filename, serialized_data, content_type)
    return filename

def extract_all_tables(igdb_credentials, s3, table_structure_dir, output_folder, bucket='video-game-statistics', content_type='application/json'):
    for entity_name, attributes in get_table_structure(table_structure_dir).items():
        data = get_game_data(fields=attributes['fields'], igdb_credentials=igdb_credentials, entity_name=entity_name)
        save_as_json(s3, bucket, data, content_type, entity_name, output_folder)

def extract_pipelines(r2_credentials, igdb_credentials, table_structure_dir, output_folder):
    s3 = connect_to_r2_using_boto3(r2_credentials)
    create_r2_bucket(s3)
    extract_all_tables(igdb_credentials, s3, table_structure_dir, output_folder)

if __name__ == '__main__':
    settings = Settings()
    extract_pipelines(
        settings.get_r2_client_credentials, settings.get_igdb_connection_credentials, 
        CONFIG_DIR, BRONZE_DIR
    )