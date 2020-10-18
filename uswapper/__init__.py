"""
A very basic wrapper for the graphqlclient that uniswap uses as their API, currently only used to get prices and
check for supported symbols
"""

import pandas as pd
from python_graphql_client import GraphqlClient
import time
import json

class USwapper:
    def __init__(self):
        self.client = GraphqlClient('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2')
        self.ass = self.getassets()

    def getprice(self, symbols):

        call = ''
        a = []

        for symbol in symbols:
            symbol = str(symbol)
            if not symbol.startswith('0x'):
                a.append(str(self.gettokenaddress(symbol)))
            else:
                a.append(symbol)
        a = json.dumps(a)
        call += f'{{tokens(where: {{id_in: {a}}})' \
                f'{{derivedETH ' \
                f'symbol' \
                f'}}}}'

        prices_dict = {}

        while True:

            try:
                prices = self.client.execute(call)['data']['tokens']
            except:
                time.sleep(5)
            else:
                for i in prices:
                    prices_dict[i['symbol']] = i['derivedETH']
                return prices_dict

    def gettokenaddress(self, symbol):
        i = self.ass[self.ass['symbol'] == str.upper(symbol)]['id'].first_valid_index()
        return self.ass.id[i]

    def gettokensymbol(self, address):
        addv = self.ass[self.ass['id'] == address]['symbol']
        addv.reset_index(inplace=True, drop=True)
        return str.upper(addv[0])

    def getassets(self):
        n = -1
        while True:
            n += 1

            call = f'' \
                   f'{{tokens(first:1000, orderDirection: desc, orderBy: txCount, skip: {n * 1000}) ' \
                   f'{{' \
                   f'id ' \
                   f'symbol ' \
                   f'derivedETH ' \
                   f'name ' \
                   f'decimals ' \
                   f'}} ' \
                   f'}}'

            try:
                response = pd.DataFrame(self.client.execute(call)['data']['tokens'])
            except:
                time.sleep(5)
                break
            else:

                if len(response) == 0:
                    assets.reset_index(inplace=True, drop=True)
                    assets['symbol'] = assets['symbol'].str.upper()
                    return assets

                if n == 0:
                    assets = pd.DataFrame(response)
                else:
                    assets = assets.append(response)

    def isuniswapasset(self, symbol):
        return True if str.upper(symbol) in self.ass.symbol.values else False

