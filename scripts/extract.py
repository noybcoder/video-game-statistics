from dotenv import load_dotenv
from requests import post
from datetime import datetime
from utils import *
from requests.exceptions import HTTPError, JSONDecodeError
import json, time, os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import Settings
from config.paths import CONFIG_DIR

load_dotenv()

def get_query(last_id: int, fields: list, limit: int=500, entity_name: str='games', year: int=2011, month: int=1, day: int=1):
    base_query = f"""
                    fields {', '.join(fields)};
                    sort id asc;
                    where id > {last_id}
                """
    if entity_name == 'games':
        base_query += f' & first_release_date >= {int(get_timestamp(year, month, day))}'

    base_query += f'; limit {limit};'
    return base_query

def get_game_data(fields: list, limit: int=500, entity_name: str='games', year: int=2011, month: int=1, day: int=1) -> list:
    master_responses = []
    last_id = 0

    settings = Settings()

    while True:
        query = get_query(last_id, fields, limit, entity_name, year, month, day)

        try:
            response = post(
                f'https://api.igdb.com/v4/{entity_name}', 
                **{'headers': settings.get_igdb_connection_credentials, 'data': query})
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
    os.makedirs(output_folder, exist_ok=True)
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

def save_as_json(data, entity_name: str, output_folder: str='data/bronze') -> str:
    filename = get_file_name(entity_name, output_folder)
    data = get_output_data(data, entity_name)

    if not data['data']:
        print(f'No data retrieved for "{entity_name}"')
        return
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filename

if __name__ == '__main__':
    for key, value in get_table_structure(CONFIG_DIR).items():
        data = get_game_data(fields=value['fields'], entity_name=key)
        save_as_json(data=data, entity_name=key)