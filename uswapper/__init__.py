"""
A very basic wrapper for the graphqlclient that uniswap uses as their API, currently only used to get prices and
check for supported symbols
"""

import pandas as pd
from python_graphql_client import GraphqlClient


class USwapper:
    def __init__(self):
        self.client = GraphqlClient('https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2')
        self.ass = self.getassets()

    def getprice(self, symbol):
        """
        takes one token and iterates until a valid response from api was received
        parameters:
            symbol: token
        returns:
            price in eth
        """
        a = str(self.gettokenaddress(symbol))

        call = f'{{tokens(where: {{id: "{a}"}})' \
               f'{{derivedETH}}}}'
        price = float(self.client.execute(call)['data']['tokens'][0]['derivedETH'])
        return price

    def gettokenaddress(self, symbol):
        """
        takes one token and checks whether it's part of uniswap tokens, in which case it will return the token address
        parameters:
            symbol: token
        returns:
            token address
        """
        addv = self.ass[self.ass['symbol'] == str.upper(symbol)]['id']
        addv.reset_index(inplace=True, drop=True)
        return addv[0]

    def gettokensymbol(self, address):
        addv = self.ass[self.ass['id'] == address]['symbol']
        addv.reset_index(inplace=True, drop=True)
        return str.upper(addv[0])

    def getassets(self):
        """
        takes one token and checks whether it's part of uniswap tokens, in which case it will return the token address
        parameters:
            None
        returns:
            pandas dataframe containing token address, symbol, symbol name
        """
        n = -1
        while True:
            n += 1

            call = f'' \
                   f'{{tokens(first:1000, orderDirection: desc, orderBy: tradeVolumeUSD, skip: {n * 1000}) ' \
                   f'{{' \
                   f'id ' \
                   f'symbol ' \
                   f'derivedETH ' \
                   f'name ' \
                   f'decimals ' \
                   f'}} ' \
                   f'}}'

            response = pd.DataFrame(self.client.execute(call)['data']['tokens'])

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
