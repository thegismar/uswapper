'''
A very basic wrapper for the graphqlclient that uniswap uses as their API, currently only used to get prices and
check for supported symbols
'''

import time
from datetime import datetime

import pandas as pd
from python_graphql_client import GraphqlClient


class USwapper:
    def __init__(self):
        self.client = GraphqlClient( 'https://api.thegraph.com/subgraphs/name/ianlapham/uniswapv2' )

        while True:
            try:
                # since the api has all prices for tokens in weth we need the eth/usd that uniswap uses
                self.ethprice = float( self.client.execute( '{bundles{ethPrice}}' )['data']['bundles'][0]['ethPrice'] )

            except ConnectionError:
                print( 'Connection error.. Retrying' )
                time.sleep( 5 )
            else:
                break

    def getprice(self, symbol):

        if symbol in self.getassets().values:  # check if the symbol is part of uniswap tokens
            while True:
                try:
                    '''
                    So this is kinda weird, it seems for some (newer) tokens, the api returns a list of TWO eth prices, 
                    being the first one 0 and the second one having the actual price. 

                    Since the symbol is part of uniswap tracked tokens, it's gotta have a price, if it's 0 we take the 
                    2nd item of the list. 

                    This might break at any point.
                    '''

                    price = float( self.client.execute( f'{{tokens(where: {{symbol: "{symbol}"}}){{'
                                                        f'derivedETH}}}}' )['data']['tokens'][0]['derivedETH'] )

                    if price == 0:
                        price = float(
                                self.client.execute( f'{{tokens(where: {{symbol: "{symbol}"}}){{derivedETH}}}}' )[
                                    'data']['tokens'][1]['derivedETH'] )

                except ConnectionError:
                    print( 'Connection error' )
                    time.sleep( 1 )

                else:
                    return price

        else:
            return None

    def gettokenaddress(self, symbol):
        ass = self.getassets()
        addv = ass[ass['symboil'] == symbol].index.values
        return addv[0]

    def getlastupdated(self):
        ts = int( self.client.execute( f'{{transactions(first: 1, orderBy: timestamp, orderDirection: desc ){{'
                                       f'timestamp}}}}' )['data']['transactions'][0]['timestamp'] )
        value = datetime.fromtimestamp( ts )

        return f'{value:%Y-%m-%d %H:%M:%S}'

    def getassets(self):
        for i in range( 3 ):
            try:
                res = self.client.execute( f'{{tokens{{'
                                           f'id symbol name decimals}}}}' )['data']['tokens']

            except ConnectionError:
                print( 'Connection Error..' )
                time.sleep( 1 )

            else:

                ass = pd.DataFrame( res )
                ass.set_index( 'id', inplace=True )
                return ass
