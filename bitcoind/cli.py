import os, json


def getBlockHeight():
  cmd = "bitcoin-cli getblockchaininfo"
  blockchain_info = os.popen(cmd).read()
  blockchain_info_json = json.loads(blockchain_info)
  return blockchain_info_json['blocks']

def getBlock(satpoint):
  satpoint_offset = len(satpoint) - 64
  get_raw_tx = "bitcoin-cli getrawtransaction " + satpoint[:-satpoint_offset] + " true"
  raw_tx = os.popen(get_raw_tx).read()
  tx_json = json.loads(raw_tx)
  block_hash = tx_json['blockhash']
  get_block_header = "bitcoin-cli getblockheader " + block_hash
  block_header = os.popen(get_block_header).read()
  block_header_json = json.loads(block_header)
  return block_header_json['height']