import sys
import asyncio
import logging
from app import config
from binance.enums import *
from binance.client import AsyncClient

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
vault = config.ConfigClient()

class AsyncoClient:
    # * #######################################################################
    # * Class initialization  
    async def main(self):

        client = await AsyncClient.create()
        exchange_info = await client.get_exchange_info()
        tickers = await client.get_all_tickers()
        await client.close_connection() 
        return tickers

    async def async_get_data(self, coin_pair): 
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET)  
        coin_price = 0
        btc_balance = 0
        btc_price = 0
        symbol_info = None
        try:
            symbol_ticker = await binance_client.get_symbol_ticker(symbol=coin_pair)
            coin_price = symbol_ticker['price']
            margin_account = await binance_client.get_margin_account()
            btc_balance = margin_account['totalNetAssetOfBtc']
            symbol_ticker = await binance_client.get_symbol_ticker(symbol="BTCUSDT")
            btc_price = symbol_ticker['price']
            symbol_info = await binance_client.get_symbol_info(symbol=coin_pair)
            btc_balance = float(btc_balance)
            btc_price = float(btc_price)
            open_margin_orders = await binance_client.get_open_margin_orders()
            await binance_client.close_connection() 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return coin_price, btc_balance, btc_price, symbol_info, margin_account, open_margin_orders

    async def get_usdt_balance(self):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        btc_balance = await binance_client.get_margin_account()['totalNetAssetOfBtc']
        btc_balance = float(btc_balance)
        btc_rate = await binance_client.get_symbol_ticker(symbol="BTCUSDT")['price']
        btc_rate = float(btc_rate)
        usdt_balance = round(btc_balance * btc_rate, 0)
        await binance_client.close_connection() 
        return int(usdt_balance)

    # * #######################################################################
    # * Function create_long_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    async def create_margin_order_entry_long(self, quantity, coinpair):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try:
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)
            await binance_client.close_connection() 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function create_short_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    async def create_margin_order_entry_short(self, quantity, coinpair):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try:
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)  
            await binance_client.close_connection()             
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function create_long_stop_loss_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order 
    async def create_long_stop_loss_order(self, coinpair, quantity, price, trigger_condition ):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try:
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_SELL, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC) 
            await binance_client.close_connection()           
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function create_short_stop_loss_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order  
    async def create_short_stop_loss_order(self, coinpair, quantity, price, trigger_condition ):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try:
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_BUY, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)      
            await binance_client.close_connection()         
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function cancel_margin_order implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.cancel_margin_order
    async def cancel_margin_order(self, coin_pair, order_id):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        try:
            #get open margin orders
            order = await binance_client.cancel_margin_order(symbol=coin_pair,orderId=order_id)
            await binance_client.close_connection() 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function create_exit_long_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order  
    async def create_exit_long_order(self, coinpair, quantity):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try:            
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)    
            await binance_client.close_connection()       
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function create_exit_short_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order  
    async def create_exit_short_order(self, coinpair, quantity):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try: 
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)      
            await binance_client.close_connection()   
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order
    
    # * #######################################################################
    # * Function get_open_margin_orders implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_open_margin_orders
    async def get_open_margin_orders(self):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        open_margin_orders = None
        try:
            #get open margin orders
            open_margin_orders = await binance_client.get_open_margin_orders()
            await binance_client.close_connection() 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_margin_orders


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
