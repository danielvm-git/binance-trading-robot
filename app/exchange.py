from app import config
import sys
import math
import logging
from datetime import datetime
from binance.enums import *
from binance.client import Client
import firebase_admin
from firebase_admin import firestore

# * ###########################################################################
# * LOGGING INSTATIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG INSTATIATION RETURNING ON CONSOLE
# * ###########################################################################
vault = config.ConfigClient()

# * ###########################################################################
# * LOGGING INSTATIATION RETURNING ON CONSOLE
# * ###########################################################################
logger = logging.getLogger(__name__)
firebase_admin.initialize_app()

# * ###########################################################################
# * Class ExchangeClient
class ExchangeClient:
    # * #######################################################################
    # * Class initialization
    def __init__(self):
        self.RISK_FACTOR = 0.01
        self.binance_client = Client(vault.API_KEY, vault.API_SECRET)
    
    # * #######################################################################
    # * Function get_account_overview implements the original API method
    # * https://bit.ly/binanceCode#binance.client.Client.get_margin_account
    def get_account_overview(self):
        try:
            account_overview = self.binance_client.get_margin_account()
            position_size = float (account_overview["totalAssetOfBtc"])
            margin_level = float (account_overview["marginLevel"])
            margin_level = round(margin_level,2)
            symbol = "BTCUSDT"
            margin_price_index = self.get_margin_price_index(symbol)
            position_value_in_dollar = self.calculate_position_value_in_dollar(margin_price_index,position_size)
            account_overview["position_value_in_dollar"] = "${:,.2f}".format(position_value_in_dollar)
            account_overview["tradeEnabled"] = str(account_overview["tradeEnabled"])
            account_overview["transferEnabled"] = str(account_overview["transferEnabled"])
            account_overview["borrowEnabled"] = str(account_overview["borrowEnabled"])
            account_overview["marginLevel"] = str(margin_level)
            logger.debug("👇👇👇👇👇 - account_overview - 👇👇👇👇👇 ")        
            logger.debug(account_overview)
            logger.debug("👆👆👆👆👆 - account_overview - 👆👆👆👆👆 ") 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return account_overview

    # * #######################################################################
    # * Function get_open_margin_orders implements the original API method 
    # * https://bit.ly/binanceCode#binance.client.Client.get_open_margin_orders
    def get_open_margin_orders(self):
        try:
            open_margin_orders = self.binance_client.get_open_margin_orders()
            for open_margin_order in open_margin_orders:
                time = int(open_margin_order["time"])
                time = datetime.fromtimestamp(time/1000)
                time = time.strftime("%m/%d/%Y, %H:%M:%S")
                updateTime = int(open_margin_order["updateTime"])
                updateTime = datetime.fromtimestamp(updateTime/1000)
                updateTime = updateTime.strftime("%m/%d/%Y, %H:%M:%S")
                open_margin_order["time"] = time
                open_margin_order["updateTime"] = updateTime
            logger.debug("👇👇👇👇👇 - open_margin_orders - 👇👇👇👇👇 ")        
            logger.debug(open_margin_orders)
            logger.debug("👆👆👆👆👆 - open_margin_orders - 👆👆👆👆👆 ") 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_margin_orders

    # * #######################################################################
    # * Function get_open_positions
    def get_open_positions(self,margin_account):
        try:
            user_assets = margin_account["userAssets"]
            open_positions = []
            for asset in user_assets:
                position_size = float (asset["netAsset"])
                if position_size != 0:
                    open_positions.append(asset)
            logger.debug("👇👇👇👇👇 - open_positions - 👇👇👇👇👇 ")        
            logger.debug(open_positions)
            logger.debug("👆👆👆👆👆 - open_positions - 👆👆👆👆👆 ")    
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_positions
    
    # * #######################################################################
    # * Function get_open_positions
    def has_stop_loss(self,open_positions,open_margin_orders):
        try:
            checked_open_positions = []
            for open_position in open_positions:
                position_size = float (open_position["netAsset"])
                symbol = open_position["asset"]
                symbol = symbol + "USDT"
                margin_price_index = self.get_margin_price_index(symbol)
                position_value_in_dollar = self.calculate_position_value_in_dollar(margin_price_index,position_size)
                position_value_in_dollar = "${:,.2f}".format(position_value_in_dollar)
                if position_size != 0:
                    open_position["has_stop_loss"] = "false"
                    for open_margin_order in open_margin_orders:
                        open_margin_symbol = open_margin_order["symbol"]
                        open_margin_symbol = open_margin_symbol.replace("USDT","")
                        open_position_symbol = open_position["asset"]
                        if open_position_symbol == open_margin_symbol: 
                            open_margin_order_size = float (open_margin_order["origQty"])
                            if position_size == open_margin_order_size:
                                open_position["has_stop_loss"] = "true"
                open_position["position_value_in_dollar"] = position_value_in_dollar
                open_position["icon_has_stop_loss"] = "true"
                checked_open_positions.append(open_position) 
            checked_open_positions.sort(key=lambda x: x["asset"], reverse=False) 
            logger.debug("👇👇👇👇👇 - checked_open_positions - 👇👇👇👇👇 ")        
            logger.debug(checked_open_positions)
            logger.debug("👆👆👆👆👆 - checked_open_positions - 👆👆👆👆👆 ")    
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return checked_open_positions

    # * #######################################################################
    # * Function get_margin_price_index
    def get_margin_price_index(self,symbol):
        try:
            if symbol == "USDTUSDT":
                price = 1
            else:
                price_index = self.binance_client.get_margin_price_index(symbol=symbol)
                price = price_index["price"]
            logger.debug("👇👇👇👇👇 - price - 👇👇👇👇👇 ")        
            logger.debug(price)
            logger.debug("👆👆👆👆👆 - price - 👆👆👆👆👆 ")    
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return price

    # * #######################################################################
    # * Function calculate_position_value_in_dollar
    def calculate_position_value_in_dollar(self,price, size):
        try:
            position_value_in_dollar = float(price) * float(size)
            position_value_in_dollar = round(position_value_in_dollar,2)
            logger.debug("👇👇👇👇👇 - price_index - 👇👇👇👇👇 ")        
            logger.debug(position_value_in_dollar)
            logger.debug("👆👆👆👆👆 - price_index - 👆👆👆👆👆 ")    
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return position_value_in_dollar
    
    def get_usdt_balance(self):
        btc_balance = float(self.binance_client.get_margin_account()['totalNetAssetOfBtc'])
        btc_rate = float((self.binance_client.get_symbol_ticker(symbol="BTCUSDT")['price']))
        usdt_balance = round(btc_balance * btc_rate, 0)
        return int(usdt_balance)

    def portion_size(self, account_balance, stop_limit_percentage):
        risk_amount = account_balance * self.RISK_FACTOR
        portion_size = risk_amount / stop_limit_percentage
        return round(portion_size, 2)
    
    def convert_portion_size_to_quantity(self, coin_pair, portion_size):
        try:

            coin_rate = float((self.binance_client.get_symbol_ticker(symbol=coin_pair)['price']))
            quantity = portion_size / coin_rate
            return float(quantity)

        except Exception as e:
            print("an exception occured - {}".format(e))
    
    def get_tick_and_step_size(self, symbol):
        tick_size = None
        step_size = None
        symbol_info = self.binance_client.get_symbol_info(symbol)
        for filt in symbol_info['filters']:
            if filt['filterType'] == 'PRICE_FILTER':
                tick_size = float(filt['tickSize'])
            if filt['filterType'] == 'LOT_SIZE':
                step_size = float(filt['stepSize'])
        return tick_size, step_size

        # Round the quantity or price range, with the actual allowed decimals
    def rounding_exact_quantity(self, quantity, step_size):
        print("stepSize", step_size)
        step_size = int(math.log10(1 / float(step_size)))
        quantity = math.floor(float(quantity) * 10 ** step_size) / 10 ** step_size
        quantity = "{:0.0{}f}".format(float(quantity), step_size)
        return str(int(quantity)) if int(step_size) == 0 else quantity

    def long_order(self, quantity, coinpair):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)              

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    def short_order(self, quantity, coinpair):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)              

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order
    
    def set_long_stop_loss(self, coinpair, quantity, price, trigger_condition ):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_SELL, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)             

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order
    
    def set_short_stop_loss(self, coinpair, quantity, price, trigger_condition ):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_BUY, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)             

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    def exit_long(self, coinpair, quantity):
        order = None
        try:            
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)           

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    def exit_short(self, coinpair, quantity):
        order = None
        try: 
            logger.debug("👇👇👇👇👇 - exit_short - 👇👇👇👇👇 ")        
            logger.debug(coinpair)
            logger.debug(quantity)
            logger.debug("👆👆👆👆👆 - exit_short - 👆👆👆👆👆 ")            
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)      
            logger.debug("👇👇👇👇👇 - exit_short - 👇👇👇👇👇 ")        
            logger.debug(order)
            logger.debug("👆👆👆👆👆 - exit_short - 👆👆👆👆👆 ")      

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    def check_is_sl_hit(self, coinpair):
        order_id_list = []
        quantity = 0
        asset = coinpair.replace("USDT","")
        try:
            # TODO testar quando não tem ordem aberta
            account_overview = self.get_account_overview()
            open_positions = self.get_open_positions(account_overview)
            open_orders = self.get_open_margin_orders()
            
            for open_order in  open_orders:
                if open_order["symbol"] == coinpair:
                    order_id_list.append(open_order["orderId"])                    
            for open_position in open_positions:
                if open_position["asset"] == asset:
                    quantity = quantity + float(open_position["netAsset"])
            for order_id in order_id_list:
                self.binance_client.cancel_margin_order(symbol=coinpair,orderId=order_id)

        except Exception as e:
                logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return quantity

    def set_debug(self, method):
        
        db = firestore.Client()
        newActivity = db.collection(u'debug').document()
        now = datetime.now()
        logger.debug("👇👇👇👇👇 - newActivity - 👇👇👇👇👇 ")        
        logger.debug(method)
        logger.debug("👆👆👆👆👆 - newActivity - 👆👆👆👆👆 ")      

        try:
            newActivity.set(
                {
                    u'text': 'New activity',
                    u'method': method,
                    u'time': now.strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            print(newActivity)
        }
    
    def set_stop_loss(self, order_response):
        
        db = firestore.Client()
        stop_loss_order = db.collection(u'stop_loss_order').document()
        now = datetime.now()
        logger.debug("👇👇👇👇👇 - stop_loss_order - 👇👇👇👇👇 ")        
        logger.debug(order_response)
        logger.debug("👆👆👆👆👆 - stop_loss_order - 👆👆👆👆👆 ")      

        try:
            stop_loss_order.set(
                {
                    u'order_response': order_response,
                    u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            print(stop_loss_order)
        }

    def set_order(self, order_response):
        
        db = firestore.Client()
        entry_order = db.collection(u'entry_order').document()
        now = datetime.now()
        logger.debug("👇👇👇👇👇 - set_order - 👇👇👇👇👇 ")        
        logger.debug(order_response)
        logger.debug("👆👆👆👆👆 - set_order - 👆👆👆👆👆 ")      

        try:
            entry_order.set(
                {
                    u'order_response': order_response,
                    u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            print(entry_order)
        }
