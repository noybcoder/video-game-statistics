from datetime import datetime, timezone
import inflect, os, json

def get_timestamp(year: int, month: int, day: int):
    return datetime(year, month, day, 0, 0, 0, tzinfo=timezone.utc).timestamp()

def get_singular_entity_name(attribute: str) -> str:
    p = inflect.engine()
    singular = p.singular_noun(attribute)
    if singular:
        return singular
    return attribute

def get_table_structure(file_path, file_name='data_structure.json'):
    file_path = os.path.join(file_path, file_name)
    with open(file_path, 'r') as f:
        return json.load(f)