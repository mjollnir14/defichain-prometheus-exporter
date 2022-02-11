#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import time
import subprocess
import sys
from prometheus_client import start_http_server, Gauge, Counter
from dateutil import parser
from datetime import datetime; from dateutil.relativedelta import *; from dateutil.tz import *

# General vars
DEFICHAIN_CLI_PATH = '/home/defichain/.defi/bin/defi-cli'
POLL_INTERVAL = 14       # In seconds

# Create Prometheus metrics to track defichaind stats.
DEFICHAIN_VERSION = Gauge('defichain_version', 'defid version')
DEFICHAIN_BLOCKS = Gauge('defichain_blocks', 'Block height')
DEFICHAIN_IS_OPERATOR = Gauge('defichain_is_operator', 'isOperator bool')
DEFICHAIN_GENERATE = Gauge('defichain_generate', 'node generate bool')
DEFICHAIN_STATE = Gauge('defichain_state', 'node state bool')
DEFICHAIN_MINTEDBLOCKS = Gauge('defichain_mintedblocks', 'minted blocks since masternode creation')
DEFICHAIN_TM1 = Gauge('defichain_tm1', 'target multiplier 1')
DEFICHAIN_TM2 = Gauge('defichain_tm2', 'target multiplier 2')
DEFICHAIN_TM3 = Gauge('defichain_tm3', 'target multiplier 3')
DEFICHAIN_TM4 = Gauge('defichain_tm4', 'target multiplier 4')

DEFICHAIN_DELTA_LASTBLOCK_ATTEMPT = Gauge('defichain_delta_lastblock_attempt', 'Elapsed seconds since last block creation attempt. Should be less than 2 seconds')

#DEFICHAIN_PEERS = Gauge('defichain_peers', 'Number of peers')
#DEFICHAIN_UPTIME = Gauge('defichain_uptime', 'Number of seconds the Defichain daemon has been running')

#DEFICHAIN_MEMPOOL_BYTES = Gauge('defichain_mempool_bytes', 'Size of mempool in bytes')
#DEFICHAIN_MEMPOOL_SIZE = Gauge('defichain_mempool_size', 'Number of unconfirmed transactions in mempool')


#DEFICHAIN_TOTAL_BYTES_RECV = Gauge('defichain_total_bytes_recv', 'Total bytes received')
#DEFICHAIN_TOTAL_BYTES_SENT = Gauge('defichain_total_bytes_sent', 'Total bytes sent')

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
         minting_info = defichain('getmintinginfo')

         DEFICHAIN_VERSION.set(versioninfo['numericVersion'])
         DEFICHAIN_BLOCKS.set(blockcount)
         DEFICHAIN_IS_OPERATOR.set(minting_info['isoperator'])

         masternodes = minting_info['masternodes']

         generate = masternodes[0]['generate']

         if generate is None:
             print('Error parsing generate item')
         elif generate:
             DEFICHAIN_GENERATE.set(1)
         else:
             DEFICHAIN_GENERATE.set(0)

         state = masternodes[0]['state']

         if state is None:
             print('Error parsing generate item')
         elif state == 'ENABLED':
             DEFICHAIN_STATE.set(1)
         else:
             DEFICHAIN_STATE.set(0)

         mintedblocks = masternodes[0]['mintedblocks']
         DEFICHAIN_MINTEDBLOCKS.set(mintedblocks)

         targetMultipliers = masternodes[0]['targetMultipliers']
         tm1 = targetMultipliers[0]
         tm2 = targetMultipliers[1]

         DEFICHAIN_TM1.set(tm1)
         DEFICHAIN_TM2.set(tm2)

         lastblockcreationattempt_iso8601 = masternodes[0]['lastblockcreationattempt']
         lastblockcreationattempt = parser.parse(lastblockcreationattempt_iso8601)

         time_now = datetime.now(tzlocal())
         delta = relativedelta(time_now, lastblockcreationattempt).normalized()

         delta_lastblock_attempt = delta.days*3600*24+delta.hours*3600+delta.minutes*60+delta.seconds+delta.microseconds/1000000
         DEFICHAIN_DELTA_LASTBLOCK_ATTEMPT.set(delta_lastblock_attempt)

         time.sleep(POLL_INTERVAL)

if __name__ == '__main__':
    main()
