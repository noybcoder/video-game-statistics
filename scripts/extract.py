from requests import post
from datetime import datetime, timezone
from data_structure import GAME_DATA
import json, time, os

def get_timestamp(year: int, month: int, day: int):
    return datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc).timestamp()

def get_query(last_id:int, fields: list, limit: int=500, entity_name: str='games', year: int=2011, month: int=1, day: int=1):
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

    credentials = {'Client-ID': 'jlb80m30qhtkcbf11vnswcga1xe1t7', 'Authorization': 'Bearer i2mvc234p8zowc6xgy4ejebnm7t3wc'}

    while True:
        query = get_query(last_id, fields, limit, entity_name, year, month, day)
        
        response = post(
            f'https://api.igdb.com/v4/{entity_name}', 
            **{'headers': credentials, 'data': query})

        game_data = response.json()

        if not game_data:
            print("No more response.")
            break

        last_id = game_data[-1]['id']

        print ("response: %s" % str(game_data))
        master_responses.extend(game_data)
        time.sleep(0.25)

    return master_responses

def get_file_name(entity_name, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    return f'{output_folder}/{entity_name}_raw_{timestamp}.json'

def get_output_data(data, entity_name):
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

def save_as_json(data, entity_name, output_folder='data/landing'):
    filename = get_file_name(entity_name, output_folder)
    data = get_output_data(data, entity_name)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return filename

if __name__ == '__main__':

    for key, value in GAME_DATA.items():
        data = get_game_data(fields=value['fields'], entity_name=key)
        save_as_json(data=data, entity_name=key)