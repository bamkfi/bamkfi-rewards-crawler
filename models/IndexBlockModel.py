import json, requests, math
import MySQLdb
from config import config

personal_server_url = config.get('personal_server_url')
personal_header = {'Authorization': f"Bearer {config.get('personal_api_token')}"}
brc20_api_server_url = config.get('brc20_api_server_url')
rune_api_server_url = config.get('rune_api_server_url')
ord_server_header = {'Accept': 'application/json'}
ord_server_url = config.get('ord_server_url')
    
class IndexBlockModel(object):
    def __init__(self, block):
        self.block = block
        self.synthetic_balances_before = []
        self.synthetic_balances_after = []
        self.balances_changes = []
        self.circulation = 0
        self.rewards = []
    
    def get_addresses_with_balances(self):
        prior_block = self.block - 1
        response = requests.get(f"{personal_server_url}balances/getBalancesByAddress&block={prior_block}", headers=personal_header)
        jsonRes = response.json()
        self.synthetic_balances_before = jsonRes['balances']
    
    def get_balance_changes(self):
        response = requests.get(f"{brc20_api_server_url}v1/brc20/activity_on_block?block_height={self.block}")
        jsonRes = response.json()

        changes = []

        # get brc20 events
        for event in jsonRes['result']:
            if event['original_tick'].lower() == '$NUSD'.lower():
                if event['event_type'] == 'mint-inscribe':
                    changes.append({
                        "address": event['minted_wallet'], #add
                        "change": int(int(event['amount']) / 1000000000000000000)
                    })
                elif event['event_type'] == 'transfer-transfer':
                    changes.append({
                        "address": event['source_wallet'], #subtract
                        "change": int(int(event['amount']) / -1000000000000000000)
                    })
                    changes.append({
                        "address": event['spent_wallet'], # add
                        "change": int(int(event['amount']) / 1000000000000000000)
                    })
        
        # get rune events
        response = requests.get(f"{rune_api_server_url}v1/runes/activity_on_block?block_height={self.block}")
        jsonRes = response.json()
        for event in jsonRes['result']:
            if event['rune_id'] == '845005:178':
                if event['outpoint'] == None: # mint, new allocation, burn
                    if event['event_type'] == "new-allocation": #add
                        changes.append({
                            "address": "bc1pg9afu20tdkmzm40zhqugeqjzl5znfdh8ndns48t0hnmn5gu7uz5saznpu9",
                            "change": int(event['amount'])
                        })
                else:
                    url = f"{ord_server_url}output/{event['outpoint']}"
                    output_res = requests.get(url, headers=ord_server_header)
                    json_output_res = output_res.json()
                    if event['event_type'] == "input": #subtract
                        changes.append({
                            "address": json_output_res['address'],
                            "change": int(int(event['amount']) * -1)
                        })
                    elif event['event_type'] == "output": #add
                        changes.append({
                            "address": json_output_res['address'],
                            "change": int(event['amount'])
                        })
        self.balances_changes=changes
    
    def update_balances_with_changes(self):
        self.synthetic_balances_after = self.synthetic_balances_before
        if len(self.balances_changes) > 0:
            for change in self.balances_changes:
                found=False
                for i in range(0, len(self.synthetic_balances_after)):
                    if change['address'] == self.synthetic_balances_after[i]['address']:
                        self.synthetic_balances_after[i]['amount']=change['change']+self.synthetic_balances_after[i]['amount']
                        found=True
                        break
                if found != True:
                    # was never found so append
                    self.synthetic_balances_after.append({
                        "address": change['address'],
                        "amount": change['change']
                    })
    
    def get_all_in_circulation(self):
        circulation = 0
        for balance in self.synthetic_balances_after:
            if balance['address'] != 'bc1pg9afu20tdkmzm40zhqugeqjzl5znfdh8ndns48t0hnmn5gu7uz5saznpu9':
                circulation+=balance['amount']
        self.circulation = circulation
    
    def calculate_rewards(self):
        total_rewards = 0
        rewards = []
        if self.circulation != 0:
            for balance in self.synthetic_balances_after:
                if balance['address'] != 'bc1pg9afu20tdkmzm40zhqugeqjzl5znfdh8ndns48t0hnmn5gu7uz5saznpu9':
                    total_rewards+=math.floor((float(balance['amount']) / float(self.circulation) * float(31250)))
                    rewards.append({
                        "address": balance['address'],
                        "amount":  math.floor((float(balance['amount']) / float(self.circulation) * float(31250)))
                    })
            rewards.append({
                "address": "foundation",
                "amount": 31250 - total_rewards
            })
        self.rewards = rewards

    def send(self, reward_balances_start_block):
        db = MySQLdb.connect(user="root")
        c = db.cursor()
        c.execute("USE bamk")
        for balance in self.synthetic_balances_after:
            c.execute("""INSERT INTO BALANCES (address, amount, block)
                VALUES (%s, %s, %s)""", (balance['address'], balance['amount'], self.block))
        
        if self.block >= reward_balances_start_block:
            for reward in self.rewards:
                c.execute("""INSERT INTO REWARD (address, amount, block)
                    VALUES (%s, %s, %s)""", (reward['address'], reward['amount'], self.block))

        db.commit()
        db.close()
