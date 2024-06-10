# Bamk.fi Rewards Crawler

Bamk.fi Rewards Crawler is the first implementation of the rewards indexer thats keeps track of BAMK rewards for each address by keeping track of synthetic dollar holdings per block.

## Server Requirements
- bitcoin-cli is running on port of your choice
- ord is running on port of your choice
- OPI - Following OPI Protocol's are running
  - Main
    - Index
  - Runes
    - Index
    - API
  - Brc20
    - Index
    - API
- Bamk.fi reward crawler also interacts with 'personal_server'
  - This is where we store synthetic dollar balances per block as well as rewards per address for each block
  - You could create your own implementation:

```sql
CREATE TABLE `BALANCES` (
  `address` varchar(64) NOT NULL,
  `amount` bigint(11) NOT NULL,
  `block` int(11) NOT NULL,
  PRIMARY KEY (`address`, `block`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `REWARD` (
  `address` varchar(64) NOT NULL,
  `amount` bigint(11) NOT NULL,
  `block` int(11) NOT NULL,
  PRIMARY KEY (`address`, `block`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
```

The API that exposes the data in the tables above does not live within this repo.
This lives within the "personal_server_url", you will have to create your own implementation to expose the data:

```python
def get_balances_by_address_manager(block):
    balances = BALANCES.query.filter(BALANCES.block == block).all()

    get_balances_response = GetBalancesByAddressAtBlockModel()
    get_balances_response.build_balances(balances, block)

    return get_balances_response.toJSON()



def get_leaderboard_manager(block):
  block_height = block
  if block_height == None:
    block_height = db.session.execute(text("SELECT MAX(block) from REWARD")).fetchone()[0]

  rewards = db.session.execute(text("SELECT address, SUM(amount) AS AMOUNT from REWARD where block <= :block GROUP BY address ORDER BY amount DESC"), {"block": block_height})

  leaderboard = GetLeaderboardModel(block_height)

  for reward in rewards:
    leaderboard.rewards.append({
      "address": reward.address,
      "amount": int(reward.AMOUNT)
    })

  return leaderboard.toJSON()
```


## Usage
- Create venv
  - ```python3 -m venv <myenvname>```
- Install python requirements
  - ```pip install -r /path/to/requirements.txt```
- Ensure 'Server Requirements are squared away'
- Populate config.py file
- Run main_index.py
  - ```python3 main_index.py```
  - Can send it to the background like:
    - ```nohup python3 main_index.py &```


## Contributing

Pull requests are welcome. 
