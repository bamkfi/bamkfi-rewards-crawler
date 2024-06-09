import requests
from config import config

ord_server_url = config.get('ord_server_url')
ord_server_header = {'Accept': 'application/json'}

def getInscriptionsPerBlock(block):
    ids=[]
    page=0
    while True:
        response = requests.get(
            f"{ord_server_url}inscriptions/block/{block}/{page}",
            headers=ord_server_header
        )
        jsonRes = response.json()
        if jsonRes['ids']:
            ids.extend(jsonRes['ids'])
        if jsonRes['more'] == False:
            break
        page+=1
    return ids

def getInscriptionMeta(id):
    response = requests.get(
        f"{ord_server_url}inscription/{id}",
        headers=ord_server_header
    )
    return response.json()

def getInscriptionContent(id):
    response = requests.get(
        f"{ord_server_url}content/{id}",
        headers=ord_server_header
    )
    try:
        return response.json()
    except:
        return None

def getInscriptionOutput(tx, offset):
    response = requests.get(
        f"{ord_server_url}output/{tx}:{offset}",
        headers=ord_server_header
    )
    return response.json()