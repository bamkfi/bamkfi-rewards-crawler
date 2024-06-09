from models.IndexBlockModel import *
from bitcoind.cli import getBlockHeight
from api.personal import getIndexBlockHeight
from api.brc20 import getBrc20IndexBlockHeight
from api.rune import getRuneIndexBlockHeight

def index():
  balances_start_block = 843834

  # balances_start_block = 846380 only uncomment if DB hasn't been initialized
  reward_balances_start_block = 844492
  blockHeight = getBlockHeight()

  event_crawler_current_block=getIndexBlockHeight() + 1

  while event_crawler_current_block <= blockHeight:
    brc20IndexBlockHeight = getBrc20IndexBlockHeight()
    runeIndexBlockHeight = getRuneIndexBlockHeight()
    if brc20IndexBlockHeight < event_crawler_current_block or runeIndexBlockHeight < event_crawler_current_block:
      break
    print('Starting to Index: ' + str(event_crawler_current_block))
    
    index_block = IndexBlockModel(event_crawler_current_block)
    
    index_block.get_addresses_with_balances()
    index_block.get_balance_changes()
    index_block.update_balances_with_changes()

    if event_crawler_current_block >= reward_balances_start_block:
      index_block.get_all_in_circulation()
      index_block.calculate_rewards()
    
    index_block.send(reward_balances_start_block)
    event_crawler_current_block+=1 