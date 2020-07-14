'''
A very basic wrapper for the graphqlclient that uniswap uses as their API, currently only used to get prices and
check for supported symbols
'''

import json

import pandas as pd
import requests
from graphqlclient import GraphQLClient


class USwapper:
    def __init__(self):
        self.client = GraphQLClient( 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2' )

        # since the api has all prices for tokens in weth we need the eth/usd that uniswap uses
        self.ethprice = float(
                json.loads( self.client.execute( '{bundles{ethPrice}}' ) )['data']['bundles'][0]['ethPrice'] )

    def getprice(self, symbol):

        if symbol in self.getassets().values:  # check if the symbol is part of uniswap tokens

            try:
                '''
                So this is kinda weird, it seems for some (newer) tokens, the api returns a list of TWO eth prices, 
                being the first one 0 and the second one having the actual price. 

                Since the symbol is part of uniswap tracked tokens, it's gotta have a price, if it's 0 we take the 
                2nd item of the list. 

                This might break at any point.
                '''

                price = float(
                        json.loads( self.client.execute( f'{{tokens(where: {{symbol: "{symbol}"}}){{derivedETH}}}}' ) )[
                            'data']['tokens'][0]['derivedETH'] )

                if price == 0:
                    price = float( json.loads(
                            self.client.execute( f'{{tokens(where: {{symbol: "{symbol}"}}){{derivedETH}}}}' ) )['data'][
                                       'tokens'][1]['derivedETH'] )

            # TODO this should be cleaned up since return None is implemented as if it meant the symbol doesn't exist.
            except requests.exceptions.HTTPError as httpErr:
                print( "Http Error:", httpErr )
                return None
            except requests.exceptions.ConnectionError as connErr:
                print( "Error Connecting:", connErr )
                return None
            except requests.exceptions.RequestException as reqErr:
                print( "Something Else:", reqErr )
                return None
            else:
                return price
        else:
            return None

    def gettokenaddress(self, symbol):
        ass = self.getassets()
        addv = ass[ass['symbol'] == symbol].index.values
        return addv[0]

    @staticmethod
    def getassets():
        try:
            response = requests.get( 'https://api.uniswap.info/v2/assets', timeout=20 )
            response.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            print( "Http Error:", httpErr )
            return None
        except requests.exceptions.ConnectionError as connErr:
            print( "Error Connecting:", connErr )
            return None
        except requests.exceptions.RequestException as reqErr:
            print( "Something Else:", reqErr )
            return None
        else:
            ass = pd.DataFrame( response.json() ).T
            ass.set_index( 'id', inplace=True )
            ass.drop( columns=['maker_fee', 'taker_fee'], inplace=True )
            return ass
