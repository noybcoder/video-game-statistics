from requests import post
import time

# fields id, name, first_release_date, genres, game_engines;

def get_game_data(fields: list, limit: int=500, offset: int=0, data_type: str='games') -> list:
    master_responses = []

    credentials = {'Client-ID': 'jlb80m30qhtkcbf11vnswcga1xe1t7', 'Authorization': 'Bearer i2mvc234p8zowc6xgy4ejebnm7t3wc'}

    while True:
        query = f"""
            fields {', '.join(fields)};
            limit {limit};
            offset {offset};
        """
        
        response = post(
            f'https://api.igdb.com/v4/{data_type}', 
            **{'headers': credentials, 'data': query})

        game_data = response.json()

        if not game_data:
            print("No more response.")
            break

        print ("response: %s" % str(game_data))
        master_responses.extend(game_data)
        time.sleep(0.25)

        offset += limit

    return master_responses

get_game_data(['id', 'name', 'first_release_date', 'genres', 'game_engines'])