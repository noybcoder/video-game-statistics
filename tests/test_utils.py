import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils import get_singular_entity_name

def test_singular_entity_name_basic():
    assert get_singular_entity_name('games') == 'game'
    assert get_singular_entity_name('genres') == 'genre'
    assert get_singular_entity_name('game_engines') == 'game_engine'
    assert get_singular_entity_name('platforms') == 'platform'

def test_singular_entity_name_companies():
    assert get_singular_entity_name('companies') == 'company'