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
        symbol_ticker = None
        symbol_ticker_BTC = None
        symbol_info = None
        margin_account = None
        open_margin_orders = None
        try:
            logger.debug("⏭️ async_get_data ⏮️")
            logger.debug("ℹ️ coin_pair:", coin_pair )

            symbol_ticker = await binance_client.get_symbol_ticker(symbol=coin_pair)
            coin_price = symbol_ticker['price']
            logger.debug("ℹ️ symbol_ticker:", symbol_ticker )
            logger.debug("ℹ️ coin_price:", coin_price )

            symbol_info = await binance_client.get_symbol_info(symbol=coin_pair)
            logger.debug("ℹ️ symbol_info:", symbol_info )
            
            margin_account = await binance_client.get_margin_account()
            btc_balance = margin_account['totalNetAssetOfBtc']
            btc_balance = float(btc_balance)
            logger.debug("ℹ️ margin_account:", margin_account )
            logger.debug("ℹ️ btc_balance:", btc_balance )

            symbol_ticker_BTC = await binance_client.get_symbol_ticker(symbol="BTCUSDT")
            btc_price = symbol_ticker_BTC['price']
            btc_price = float(btc_price)
            logger.debug("ℹ️ symbol_ticker_BTC:", symbol_ticker_BTC )
            logger.debug("ℹ️ btc_price:", btc_price )

            open_margin_orders = await binance_client.get_open_margin_orders()
            logger.debug("ℹ️ open_margin_orders:", open_margin_orders )
            logger.debug("⏭️ async_get_data ⏮") 

            await binance_client.close_connection() 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return coin_price, btc_balance, btc_price, symbol_info, margin_account, open_margin_orders

    # * #######################################################################
    # * Function create_long_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    async def create_margin_order_entry_long(self, quantity, coinpair):
        binance_client = AsyncClient(vault.API_KEY, vault.API_SECRET) 
        order = None
        try:
            logger.debug("⏭️ create_margin_order_entry_long ⏮️")
            logger.debug("ℹ️ coin_pair:", coinpair )
            logger.debug("ℹ️ quantity:", quantity)
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)                       
            logger.debug(order)
            logger.debug("⏭️ create_margin_order_entry_long ⏮") 
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
            logger.debug("⏭️ create_margin_order_entry_short ⏮️")
            logger.debug("ℹ️ coin_pair:", coinpair )
            logger.debug("ℹ️ quantity:", quantity)
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)                           
            logger.debug(order)
            logger.debug("⏭️ create_margin_order_entry_short ⏮") 
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
            logger.debug("⏭️ create_long_stop_loss_order ⏮️")
            logger.debug("ℹ️ coin_pair:", coinpair )
            logger.debug("ℹ️ quantity:", quantity) 
            logger.debug("ℹ️ price:", price) 
            logger.debug("ℹ️ trigger_condition:", trigger_condition)
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_SELL, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)                                       
            logger.debug(order)
            logger.debug("⏭️ create_long_stop_loss_order ⏮")     
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
            logger.debug("⏭️ create_short_stop_loss_order ⏮️")
            logger.debug("ℹ️ coin_pair:", coinpair )
            logger.debug("ℹ️ quantity:", quantity) 
            logger.debug("ℹ️ price:", price) 
            logger.debug("ℹ️ trigger_condition:", trigger_condition) 
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_BUY, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)                            
            logger.debug(order)
            logger.debug("⏭️ create_short_stop_loss_order ⏮")    
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
            logger.debug("⏭️ cancel_margin_order ⏮️")
            logger.debug("ℹ️ coin_pair:", coin_pair )
            logger.debug("ℹ️ order_id:", order_id) 
            order = await binance_client.cancel_margin_order(symbol=coin_pair,orderId=order_id)              
            logger.debug(order)
            logger.debug("⏭️ cancel_margin_order ⏮")
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
            logger.debug("⏭️ create_exit_long_order ⏮️")
            logger.debug("ℹ️ coin_pair:", coinpair )
            logger.debug("ℹ️ quantity:", quantity)            
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)    
            logger.debug(order)
            logger.debug("⏭️ create_exit_long_order ⏮")
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
            logger.debug("⏭️ create_exit_short_order ⏮️")
            logger.debug("ℹ️ coin_pair:", coinpair )
            logger.debug("ℹ️ quantity:", quantity)
            order = await binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)         
            logger.debug(order)
            logger.debug("⏭️ create_exit_short_order ⏮️")    
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
            logger.debug("⏭️ get_open_margin_orders ⏮️")
            logger.debug(open_margin_orders)
            logger.debug("⏭️ get_open_margin_orders ⏮️")
            await binance_client.close_connection() 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_margin_orders


if __name__ == "__main__":

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
