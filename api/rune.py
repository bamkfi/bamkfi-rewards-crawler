import requests
from config import config
rune_api_server_url = config.get('rune_api_server_url')


def getRuneIndexBlockHeight():
    response = requests.get(
        f"{rune_api_server_url}v1/runes/activity_on_block"
    )
    res = response.json()
    return int(res['db_block_height'])