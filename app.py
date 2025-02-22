import json
import logging
import os
import random
import requests
import sys

from datetime import datetime
from environs import Env


env = Env()
env.read_env()

logs_file_path = env.str("LOGS_FILE_PATH", "./logs")
tips_file_path = env.str("TIPS_FILE_PATH", "./tips.json")
log_level = env.str("LOG_LEVEL", "INFO")
pt_panel_url = env.str("PTERODACTYL_PANEL_URL")
pt_panel_api = env.str("PTERODACTYL_PANEL_API_KEY")
pt_panel_srv = env.str("PTERODACTYL_SERVER_UUID")


# Logging configuration
log_format = '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'
logfilename = f'logs/app_{str(datetime.now().strftime("%Y_%m_%d_%H_%M_%S"))}.log'
logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)
logger = logging.getLogger(__name__)
logger.setLevel(log_level)


try:
    if not os.path.isdir(logs_file_path):
        os.makedirs('logs', exist_ok=True)
        logger.info('Logs directory created successfully')
except OSError:
    logger.error('Logs directory could not be created')


handler = logging.FileHandler(filename=logfilename, encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
logger.addHandler(handler)

if not pt_panel_url:
    logger.error('PTERODACTYL_PANEL_URL was not provided. Exiting.')
    sys.exit(1)

if not pt_panel_api:
    logger.error('PTERODACTYL_PANEL_API_KEY was not provided. Exiting.')
    sys.exit(1)

if not pt_panel_srv:
    logger.error('PTERODACTYL_SERVER_UUID was not provided. Exiting.')
    sys.exit(1)


def get_tips_json(file_path: str) -> list:
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            logger.info(f'Loaded JSON file at {file_path}')
            return data
    except FileNotFoundError:
        logger.error(f'File not found: {file_path}')
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f'Invalid JSON format in: {file_path}')
        sys.exit(1)


def main():
    tips = (get_tips_json(tips_file_path))['tips']
    url = f'{pt_panel_url}/api/client/servers/{pt_panel_srv}/command'
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {pt_panel_api}'}
    payload = {'command': f'say {random.choice(tips)}'}

    try:
        logger.info(f'Attempting to send command payload {payload}')
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        logger.info(f'Received {r.status_code} status code')
        # Logging done lets Pterodactyl know that it's ready
        logger.info('Done')
        sys.exit(0)
    except requests.exceptions.RequestException as e:
        logger.error('e')
        raise SystemExit(e)


main()
