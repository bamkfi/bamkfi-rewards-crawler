import requests
from config import config

personal_server_url = config.get('personal_server_url')
personal_header = {'Authorization': f"Bearer {config.get('personal_api_token')}"}

def getIndexBlockHeight():
    response = requests.get(
        f"{personal_server_url}reward/getLeaderboard",
        headers=personal_header
    )
    res = response.json()
    return res['block']