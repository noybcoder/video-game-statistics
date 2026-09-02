import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BRONZE_DIR = os.path.join(PROJECT_ROOT, 'data', 'bronze')
SILVER_DIR = os.path.join(PROJECT_ROOT, 'data', 'silver')
CONFIG_DIR = os.path.join(PROJECT_ROOT, 'config')