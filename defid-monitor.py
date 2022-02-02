#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import sys
from prometheus_client import start_http_server, Gauge, Counter

# General vars
POLL_TIME = 300
DEFICHAIN_CLI_PATH = '/home/defichain/.defi/bin/defi-cli'

# Create Prometheus metrics to track defichaind stats.
DEFICHAIN_VERSION = Gauge('defichain_version', 'defid version')
DEFICHAIN_BLOCKS = Gauge('defichain_blocks', 'Block height')
DEFICHAIN_DIFFICULTY = Gauge('defichain_difficulty', 'Difficulty')
DEFICHAIN_PEERS = Gauge('defichain_peers', 'Number of peers')
DEFICHAIN_HASHPS = Gauge('defichain_hashps', 'Estimated network hash rate per second')

DEFICHAIN_ERRORS = Counter('defichain_errors', 'Number of errors detected')
DEFICHAIN_UPTIME = Gauge('defichain_uptime', 'Number of seconds the Defichain daemon has been running')

DEFICHAIN_MEMPOOL_BYTES = Gauge('defichain_mempool_bytes', 'Size of mempool in bytes')
DEFICHAIN_MEMPOOL_SIZE = Gauge('defichain_mempool_size', 'Number of unconfirmed transactions in mempool')

DEFICHAIN_LATEST_BLOCK_SIZE = Gauge('defichain_latest_block_size', 'Size of latest block in bytes')
DEFICHAIN_LATEST_BLOCK_TXS = Gauge('defichain_latest_block_txs', 'Number of transactions in latest block')

DEFICHAIN_NUM_CHAINTIPS = Gauge('defichain_num_chaintips', 'Number of known blockchain branches')

DEFICHAIN_TOTAL_BYTES_RECV = Gauge('defichain_total_bytes_recv', 'Total bytes received')
DEFICHAIN_TOTAL_BYTES_SENT = Gauge('defichain_total_bytes_sent', 'Total bytes sent')

DEFICHAIN_LATEST_BLOCK_INPUTS = Gauge('defichain_latest_block_inputs', 'Number of inputs in transactions of latest block')
DEFICHAIN_LATEST_BLOCK_OUTPUTS = Gauge('defichain_latest_block_outputs', 'Number of outputs in transactions of latest block')


def defichain(cmd):
    defichain = subprocess.Popen([DEFICHAIN_CLI_PATH, cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = defichain.communicate()[0]
    return json.loads(output.decode('utf-8'))


def defichaincli(cmd):
    defichain = subprocess.Popen([DEFICHAIN_CLI_PATH, cmd], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = defichain.communicate()[0]
    return output.decode('utf-8')


def get_block(block_height):
    try:
        block = subprocess.check_output([DEFICHAIN_CLI_PATH, 'getblock', block_height])
    except Exception as e:
        print(e)
        print('Error: Can\'t retrieve block number ' + block_height + ' from defichaind.')
        return None
    return json.loads(block.decode('utf-8'))


def get_raw_tx(txid):
    try:
        rawtx = subprocess.check_output([DEFICHAIN_CLI_PATH, 'getrawtransaction', txid, '1'])
    except Exception as e:
        print(e)
        print('Error: Can\'t retrieve raw transaction ' + txid + ' from defichaind.')
        return None
    return json.loads(rawtx.decode('utf-8'))


def main():
    # Start up the server to expose the metrics.
    start_http_server(8334)
    while True:
         versioninfo = defichain('getversioninfo')
         blockcount = defichain('getblockcount')
#        chaintips = len(defichain('getchaintips'))
#        mempool = defichain('getmempoolinfo')
#        nettotals = defichain('getnettotals')
#         latest_block = get_block(str(blockcount))
#        hashps = float(defichaincli('getnetworkhashps'))

         DEFICHAIN_VERSION.set(versioninfo['numericVersion'])
         DEFICHAIN_BLOCKS.set(blockcount)
#        DEFICHAIN_PEERS.set(info['connections'])
#        DEFICHAIN_DIFFICULTY.set(info['difficulty'])
#        DEFICHAIN_HASHPS.set(hashps)

#        if info['errors']:
#            DEFICHAIN_ERRORS.inc()

#        DEFICHAIN_NUM_CHAINTIPS.set(chaintips)

#        DEFICHAIN_MEMPOOL_BYTES.set(mempool['bytes'])
#        DEFICHAIN_MEMPOOL_SIZE.set(mempool['size'])

#        DEFICHAIN_TOTAL_BYTES_RECV.set(nettotals['totalbytesrecv'])
#        DEFICHAIN_TOTAL_BYTES_SENT.set(nettotals['totalbytessent'])

#        if latest_block is not None:
#            DEFICHAIN_LATEST_BLOCK_SIZE.set(latest_block['size'])
#            DEFICHAIN_LATEST_BLOCK_TXS.set(len(latest_block['tx']))
#            inputs, outputs = 0, 0
            # counting transaction inputs and outputs requires txindex=1
            # to be enabled, which may also necessitate reindex=1 in defichain.conf
#            for tx in latest_block['tx']:

#                if get_raw_tx(tx) is not None:
#                    rawtx = get_raw_tx(tx)
#                    i = len(rawtx['vin'])
#                   inputs += i
#                    o = len(rawtx['vout'])
#                    outputs += o

#            DEFICHAIN_LATEST_BLOCK_INPUTS.set(inputs)
#            DEFICHAIN_LATEST_BLOCK_OUTPUTS.set(outputs)
    
         print('.')
         time.sleep(POLL_TIME)

if __name__ == '__main__':
    main()
