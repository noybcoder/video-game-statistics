import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

R2_OBJECT_URL_PREFIX = 'r2://video-game-statistics'
# BRONZE_DIR = os.path.join(PROJECT_ROOT, 'data', 'bronze')
# SILVER_DIR = os.path.join(PROJECT_ROOT, 'data', 'silver')
BRONZE_DIR = 'data/bronze'
SILVER_DIR = f'{R2_OBJECT_URL_PREFIX}/data/silver'
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')