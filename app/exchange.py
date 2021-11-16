from app import config
import logging
import time
import sys
from binance.enums import *
from binance.client import Client

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
vault = config.ConfigClient()

# * ###########################################################################
# * Class ExchangeClient
class ExchangeClient:
    # * #######################################################################
    # * Class initialization
    def __init__(self):
        self.binance_client = Client(vault.API_KEY, vault.API_SECRET)
        self.base_currency = "BTCUSDT"
    
    # * #######################################################################
    # * Function get_margin_account implements the original API method
    # * https://bit.ly/binanceCode#binance.client.Client.get_margin_account
    def get_margin_account(self):
        account_overview = None
        try:
            #get account overview
            account_overview = self.binance_client.get_margin_account()
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return account_overview
    
    # * #######################################################################
    # * Function get_open_margin_orders implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_open_margin_orders
    def get_open_margin_orders(self):
        try:
            #get open margin orders
            open_margin_orders = self.binance_client.get_open_margin_orders()
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_margin_orders

    # * #######################################################################
    # * Function get_margin_trades implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_margin_trades
    def get_margin_trades(self, symbol):
        margin_trades = None
        try:
            #get open margin orders
            margin_trades = self.binance_client.get_margin_trades(symbol=symbol)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 symbol 🔥")
            logger.exception(symbol)
        return margin_trades 

    # * #######################################################################
    # * Function cancel_margin_order implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.cancel_margin_order
    def cancel_margin_order(self, coin_pair, order_id):
        try:
            #get open margin orders
            self.binance_client.cancel_margin_order(symbol=coin_pair,orderId=order_id)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 coin_pair 🔥")
            logger.exception(coin_pair)
            logger.exception("🔥 order_id 🔥")
            logger.exception(order_id)
        return {
            logger.debug("Order Canceled: ", order_id)
        }  

    # * #######################################################################
    # * Function get_margin_price_index implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_margin_price_index
    def get_margin_price_index(self,symbol):
        try:
            if symbol == "USDTUSDT":
                price = 1
            else:
                price_index = self.binance_client.get_margin_price_index(symbol=symbol)
                price = price_index["price"]
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 symbol 🔥")
            logger.exception(symbol)
        return price

    # * #######################################################################
    # * Function get_symbol_info implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_symbol_info
    def get_symbol_info(self, symbol):
        try:
            #get symbol info
            symbol_info = self.binance_client.get_symbol_info(symbol)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 symbol 🔥")
            logger.exception(symbol)
        return symbol_info
    
    # * #######################################################################
    # * Function get_symbol_ticker implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_symbol_ticker
    def get_symbol_ticker(self, symbol):
        symbol_ticker = None
        try:
            #get symbol ticker
            symbol_ticker = self.binance_client.get_symbol_ticker(symbol=symbol)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 symbol 🔥")
            logger.exception(symbol)
        return symbol_ticker

    # * #######################################################################
    # * Function create_long_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    def create_long_order(self, quantity, coinpair):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 quantity 🔥")
            logger.exception(quantity)
            logger.exception("🔥 coinpair 🔥")
            logger.exception(coinpair)
        return order

    # * #######################################################################
    # * Function create_short_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    def create_short_order(self, quantity, coinpair):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)              
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥")
            logger.exception("🔥 quantity 🔥")
            logger.exception(quantity)
            logger.exception("🔥 coinpair 🔥")
            logger.exception(coinpair) 
        return order
    
    # * #######################################################################
    # * Function create_long_stop_loss_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order 
    def create_long_stop_loss_order(self, coinpair, quantity, price, trigger_condition ):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_SELL, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC, sideEffectType="AUTO_REPAY")             
        except Exception as e:
            raise e
        return order
    
    # * #######################################################################
    # * Function create_short_stop_loss_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order  
    def create_short_stop_loss_order(self, coinpair, quantity, price, trigger_condition ):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_BUY, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC, sideEffectType="AUTO_REPAY")             
        except Exception as e:
            raise e
        return order

    # * #######################################################################
    # * Function create_exit_long_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order  
    def create_exit_long_order(self, coinpair, quantity):
        order = None
        try:            
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)           
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 coinpair 🔥")
            logger.exception(coinpair)
            logger.exception("🔥 quantity 🔥")
            logger.exception(quantity)
        return order

    # * #######################################################################
    # * Function create_exit_short_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order  
    def create_exit_short_order(self, coinpair, quantity):
        order = None
        try: 
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)      
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 coinpair 🔥")
            logger.exception(coinpair)
            logger.exception("🔥 quantity 🔥")
            logger.exception(quantity)
        return order

    def sync_get_data(self, coin_pair): 
        coin_price = 0
        btc_balance = 0
        btc_price = 0
        symbol_ticker = None
        symbol_ticker_BTC = None
        symbol_info = None
        margin_account = None
        open_margin_orders = None
        try:
            logger.debug("⏭️ BEGIN OF sync_get_data ⏮️")
            logger.debug("ℹ️ coin_pair:")
            logger.debug(coin_pair)

            symbol_ticker = self.binance_client.get_symbol_ticker(symbol=coin_pair)
            coin_price = symbol_ticker['price']
            logger.debug("ℹ️ symbol_ticker:")
            logger.debug(symbol_ticker)
            logger.debug("ℹ️ coin_price:")
            logger.debug(coin_price)

            symbol_info = self.binance_client.get_symbol_info(symbol=coin_pair)
            logger.debug("ℹ️ symbol_info:")
            logger.debug(symbol_info)
            
            margin_account = self.binance_client.get_margin_account()
            btc_balance = margin_account['totalNetAssetOfBtc']
            btc_balance = float(btc_balance)
            logger.debug("ℹ️ margin_account:")
            logger.debug(margin_account)
            logger.debug("ℹ️ btc_balance:")
            logger.debug(btc_balance)

            symbol_ticker_BTC = self.binance_client.get_symbol_ticker(symbol="BTCUSDT")
            btc_price = symbol_ticker_BTC['price']
            btc_price = float(btc_price)
            logger.debug("ℹ️ symbol_ticker_BTC:")
            logger.debug(symbol_ticker_BTC)
            logger.debug("ℹ️ btc_price:")
            logger.debug(btc_price)

            open_margin_orders = self.binance_client.get_open_margin_orders()
            logger.debug("ℹ️ open_margin_orders:")
            logger.debug(open_margin_orders)
            logger.debug("⏭️ END OF sync_get_data ⏮") 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 coin_pair 🔥")
            logger.exception(coin_pair)
        return coin_price, btc_balance, btc_price, symbol_info, margin_account, open_margin_orders

    # * #######################################################################
    # * Function create_long_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    def create_margin_order_entry_long(self, quantity, coinpair):
        order = None
        try:
            logger.debug("⏭️ BEGIN OF create_margin_order_entry_long ⏮️")
            logger.debug("ℹ️ coin_pair:")
            logger.debug(coinpair)
            logger.debug("ℹ️ quantity:")
            logger.debug(quantity)
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)                       
            logger.debug("ℹ️ margin_order_entry_long:")
            logger.debug(order)
            time.sleep(5)
            logger.debug("⏭️ END OF create_margin_order_entry_long ⏮") 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 quantity 🔥")
            logger.exception(quantity)
            logger.exception("🔥 coinpair 🔥")
            logger.exception(coinpair)
        return order

    # * #######################################################################
    # * Function create_short_order using create_margin_order method from binance API
    # * https://bit.ly/binanceCode#binance.client.Client.create_margin_order
    def create_margin_order_entry_short(self, quantity, coinpair):
        order = None
        try:
            logger.debug("⏭️ BEGIN OF create_margin_order_entry_short ⏮️")
            logger.debug("ℹ️ coin_pair:")
            logger.debug(coinpair)
            logger.debug("ℹ️ quantity:")
            logger.debug(quantity)
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)                           
            logger.debug("ℹ️ margin_order_entry_short:")
            logger.debug(order)
            time.sleep(5)
            logger.debug("⏭️ END OF create_margin_order_entry_short ⏮") 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            logger.exception("🔥 quantity 🔥")
            logger.exception(quantity)
            logger.exception("🔥 coinpair 🔥")
            logger.exception(coinpair)
        return order