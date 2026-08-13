import duckdb, json, os, re


def get_latest_file(file_path, entity_name):
    files = [os.path.join(file_path, file) for file in os.listdir(file_path) if re.match(f'{entity_name}_raw.*json', file)]
    target_file = max(files, key=os.path.getctime)

    return target_file

LANDING_DIR = 'data/landing'

print(get_latest_file(LANDING_DIR, 'genres'))