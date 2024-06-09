import requests
from config import config

brc20_api_server_url = config.get('brc20_api_server_url')


def getBrc20IndexBlockHeight():
    response = requests.get(
        f"{brc20_api_server_url}v1/brc20/block_height"
    )
    return int(response.text)