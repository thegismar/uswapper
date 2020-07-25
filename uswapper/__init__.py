"""
A very basic wrapper for the graphqlclient that uniswap uses as their API, currently only used to get prices and
check for supported symbols
"""

import time

import pandas as pd
import requests
from python_graphql_client import GraphqlClient
from requests import HTTPError, Timeout, TooManyRedirects
from urllib3.exceptions import NewConnectionError


class USwapper:
    def __init__(self):
        self.client = GraphqlClient( 'https://api.thegraph.com/subgraphs/name/ianlapham/uniswapv2' )
        self.ass = self.getassets()
        while True:
            try:
                # since the api has all prices for tokens in weth we need the eth/usd that uniswap uses
                self.ethprice = float( self.client.execute( '{bundles{ethPrice}}' )['data']['bundles'][0]['ethPrice'] )

            except (HTTPError, Timeout, TooManyRedirects, NewConnectionError):
                print( 'Connection Error.. Retrying in 10 seconds' )
                time.sleep( 10 )
            else:
                break

    def getprice(self, symbol):
        """
        takes one token and iterates until a valid response from api was received
        parameters:
            symbol: token
        returns:
            price in eth
        raises :
            HTTPError, Timeout, TooManyRedirects
        """

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
                            self.client.execute( f'{{tokens(where: {{symbol: "{symbol}"}}){{derivedETH}}}}' )['data'][
                                'tokens'][1]['derivedETH'] )

            except (HTTPError, Timeout, TooManyRedirects, NewConnectionError):
                print( 'Connection Error.. Retrying in 10 seconds' )
                time.sleep( 10 )

            else:
                return price

    def gettokenaddress(self, symbol):
        """
        takes one token and checks whether it's part of uniswap tokens, in which case it will return the token address
        parameters:
            symbol: token
        returns:
            token address
        raises :
            HTTPError, Timeout, TooManyRedirects
        """
        ass = self.getassets()
        addv = ass[ass['symbol'] == symbol].index.values
        return addv[0]

    @staticmethod
    def getassets():
        """
        takes one token and checks whether it's part of uniswap tokens, in which case it will return the token address
        parameters:
            None
        returns:
            pandas dataframe containing token address, symbol, symbol name
        raises :
            HTTPError, Timeout, TooManyRedirects
        """
        while True:

            try:
                response = requests.get( 'https://api.uniswap.info/v2/assets' )
                response.raise_for_status()
            except (HTTPError, Timeout, TooManyRedirects, NewConnectionError):
                print( 'Connection Error.. Retrying in 10 seconds' )
                time.sleep( 10 )
            else:
                response = response.json()
                ass = pd.DataFrame( response )
                return ass.T

    def isuniswapasset(self, symbol):
        return True if symbol in self.ass.symbol.values else False
