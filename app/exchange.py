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
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
vault = config.ConfigClient()

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
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
        self.base_currency = "BTCUSDT"
    
    # * #######################################################################
    # * Function get_account_overview implements the original API method
    # * https://bit.ly/binanceCode#binance.client.Client.get_margin_account
    def get_account_overview(self):
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
    # * Function prepare_account_overview
    def prepare_account_overview(self,account_overview):
        try:
            #round margin level
            margin_level = float (account_overview["marginLevel"])
            margin_level = round(margin_level,2)            
            #calculate the position value in dollar
            symbol = "BTCUSDT"
            margin_price_index = self.get_margin_price_index(symbol)
            position_size = float (account_overview["totalAssetOfBtc"])
            position_value_in_dollar = self.calculate_position_value_in_dollar(margin_price_index,position_size)
            #set account overview with the string of the values
            account_overview["position_value_in_dollar"] = "${:,.2f}".format(position_value_in_dollar)
            account_overview["tradeEnabled"] = str(account_overview["tradeEnabled"])
            account_overview["transferEnabled"] = str(account_overview["transferEnabled"])
            account_overview["borrowEnabled"] = str(account_overview["borrowEnabled"])
            account_overview["marginLevel"] = str(margin_level)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return account_overview
    
    # * #######################################################################
    # * Function prepare_open_margin_orders 
    def prepare_open_margin_orders(self, open_margin_orders):
        try:
            #convert from milliseconds, set date and time for each open order
            for open_margin_order in open_margin_orders:
                time = int(open_margin_order["time"])
                time = datetime.fromtimestamp(time/1000)
                time = time.strftime("%m/%d/%Y, %H:%M:%S")
                updateTime = int(open_margin_order["updateTime"])
                updateTime = datetime.fromtimestamp(updateTime/1000)
                updateTime = updateTime.strftime("%m/%d/%Y, %H:%M:%S")
                open_margin_order["time"] = time
                open_margin_order["updateTime"] = updateTime
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_margin_orders
    
    # * #######################################################################
    # * Function calculate_position_value_in_dollar
    def calculate_position_value_in_dollar(self,price, size):
        try:
            position_value_in_dollar = float(price) * float(size)
            position_value_in_dollar = round(position_value_in_dollar,2)  
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return position_value_in_dollar
    
    # * #######################################################################
    # * Function get_open_positions
    def get_open_positions(self,margin_account):
        open_positions = []
        try:
            user_assets = margin_account["userAssets"]
            open_positions = []
            tradable_assets = []
            for asset in user_assets:
                position_size = float (asset["netAsset"])
                tradable_assets.append(asset["asset"])
                if position_size != 0:
                    open_positions.append(asset)
            logger.debug("👇👇👇👇👇 - open_positions - 👇👇👇👇👇 ")        
            logger.debug(open_positions)
            logger.debug("👆👆👆👆👆 - open_positions - 👆👆👆👆👆 ")  
            logger.debug("👇👇👇👇👇 - tradable_assets - 👇👇👇👇👇 ")        
            logger.debug(tradable_assets)
            logger.debug("👆👆👆👆👆 - tradable_assets - 👆👆👆👆👆 ") 
            self.set_tradable_assets(tradable_assets) 
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_positions    
    
    # * #######################################################################
    # * Function has_stop_loss
    def has_stop_loss(self,open_positions,open_margin_orders):
        try:
            checked_open_positions = []
            for open_position in open_positions:
                #prepare data to compare
                position_size = float (open_position["netAsset"])
                #prepare the symbol
                symbol = open_position["asset"]
                symbol = symbol + "USDT"
                #get the price of symbol
                margin_price_index = self.get_margin_price_index(symbol)
                #calculate the position side in US dollar
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
    # * Function 
    def get_usdt_balance(self):
        btc_balance = float(self.binance_client.get_margin_account()['totalNetAssetOfBtc'])
        btc_rate = float((self.binance_client.get_symbol_ticker(symbol=self.base_currency)['price']))
        usdt_balance = round(btc_balance * btc_rate, 0)
        return int(usdt_balance)

    # * #######################################################################
    # * Function 
    def portion_size(self, account_balance, stop_limit_percentage):
        risk_amount = account_balance * self.RISK_FACTOR
        portion_size = risk_amount / stop_limit_percentage
        return round(portion_size, 2), risk_amount
    
    # * #######################################################################
    # * Function 
    def convert_portion_size_to_quantity(self, coin_pair, portion_size):
        try:

            coin_rate = float((self.binance_client.get_symbol_ticker(symbol=coin_pair)['price']))
            quantity = portion_size / coin_rate
            return float(quantity), coin_rate

        except Exception as e:
            print("an exception occurred - {}".format(e))
    
    # * #######################################################################
    # * Function 
    def get_tick_and_step_size(self, symbol):
        tick_size = None
        step_size = None
        symbol_info = self.binance_client.get_symbol_info(symbol)
        for filter in symbol_info['filters']:
            if filter['filterType'] == 'PRICE_FILTER':
                tick_size = float(filter['tickSize'])
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
        return tick_size, step_size

    # * #######################################################################
    # * Function     # Round the quantity or price range, with the actual allowed decimals
    def rounding_exact_quantity(self, quantity, step_size):
        print("stepSize", step_size)
        step_size = int(math.log10(1 / float(step_size)))
        quantity = math.floor(float(quantity) * 10 ** step_size) / 10 ** step_size
        quantity = "{:0.0{}f}".format(float(quantity), step_size)
        return str(int(quantity)) if int(step_size) == 0 else quantity

    # * #######################################################################
    # * Function 
    def long_order(self, quantity, coinpair):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)              

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function 
    def short_order(self, quantity, coinpair):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="MARGIN_BUY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)              

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order
    
    # * #######################################################################
    # * Function 
    def set_long_stop_loss(self, coinpair, quantity, price, trigger_condition ):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_SELL, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)             

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order
    
    # * #######################################################################
    # * Function 
    def set_short_stop_loss(self, coinpair, quantity, price, trigger_condition ):
        order = None
        try:
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, price=price, stopPrice=trigger_condition, side=SIDE_BUY, type=ORDER_TYPE_STOP_LOSS_LIMIT, timeInForce=TIME_IN_FORCE_GTC)             

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function 
    def exit_long(self, coinpair, quantity):
        order = None
        try:            
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_SELL, type=ORDER_TYPE_MARKET)           

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function 
    def exit_short(self, coinpair, quantity):
        order = None
        try: 
            logger.debug("👇👇👇👇👇 - exit_short - 👇👇👇👇👇 ")        
            logger.debug(coinpair)
            logger.debug(quantity)
            logger.debug("👆👆👆👆👆 - exit_short - 👆👆👆👆👆 ")            
            order = self.binance_client.create_margin_order(symbol=coinpair, quantity=quantity, sideEffectType="AUTO_REPAY", side=SIDE_BUY, type=ORDER_TYPE_MARKET)      
            logger.debug("👇👇👇👇👇 - exit_short - 👇👇👇👇👇 ")        
            logger.debug(order)
            logger.debug("👆👆👆👆👆 - exit_short - 👆👆👆👆👆 ")      

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return order

    # * #######################################################################
    # * Function 
    def check_is_sl_hit(self, coinpair):
        order_id_list = []
        quantity = 0
        asset = coinpair.replace("USDT","")
        try:
            # TODO test when there is no open order
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
    
    # * #######################################################################
    # * Function 
    def check_is_sl_hit_short(self, coinpair):
        order_id_list = []
        quantity = 0
        asset = coinpair.replace("USDT","")
        try:
            # TODO test when there is no open order
            account_overview = self.get_account_overview()
            open_positions = self.get_open_positions(account_overview)
            open_orders = self.get_open_margin_orders()
            
            for open_order in  open_orders:
                if open_order["symbol"] == coinpair:
                    order_id_list.append(open_order["orderId"])                    
            for open_position in open_positions:
                if open_position["asset"] == asset:
                    quantity = quantity + float(open_position["borrowed"])
            for order_id in order_id_list:
                self.binance_client.cancel_margin_order(symbol=coinpair,orderId=order_id)

        except Exception as e:
                logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return quantity

    # * #######################################################################
    # * Function     
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

    # * #######################################################################
    # * Function 
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

    # * #######################################################################
    # * Function 
    def set_account_overview(self, account_overview):
        
        db = firestore.Client()
        entry_order = db.collection(u'account_overview').document()
        now = datetime.now()
        logger.debug("👇👇👇👇👇 - account_overview - 👇👇👇👇👇 ")        
        logger.debug(account_overview)
        logger.debug("👆👆👆👆👆 - account_overview - 👆👆👆👆👆 ")      

        try:
            entry_order.set(
                {
                    u'account_overview': account_overview,
                    u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            print(account_overview)
        }

    # * #######################################################################
    # * Function     
    def set_open_margin_orders(self, open_margin_orders):
        
        db = firestore.Client()
        self.delete_open_margin_orders()
        open_margin_orders_collection = db.collection(u'open_margin_orders').document()
        logger.debug("👇👇👇👇👇 - set_open_margin_orders - 👇👇👇👇👇 ")        
        logger.debug(open_margin_orders_collection)
        logger.debug("👆👆👆👆👆 - set_open_margin_orders - 👆👆👆👆👆 ")      

        try:
            open_margin_orders_collection.set(
                {
                    u'open_margin_orders': open_margin_orders
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            logger.debug("👇👇👇👇👇 - set_open_margin_orders successful - 👇👇👇👇👇 ")   
        }

    # * #######################################################################
    # * Function 
    def set_checked_open_position(self, open_position):
            
        db = firestore.Client()        
        checked_open_positions_collection = db.collection(u'checked_open_positions').document()
        logger.debug("👇👇👇👇👇 - set_checked_open_positions - 👇👇👇👇👇 ")        
        logger.debug(open_position)
        logger.debug("👆👆👆👆👆 - set_checked_open_positions - 👆👆👆👆👆 ")
        now = datetime.now()      

        try:
            checked_open_positions_collection.set(
                {
                    u'asset': open_position['asset'] ,
                    u'position_value_in_dollar': open_position['position_value_in_dollar'] ,
                    u'netAsset': open_position['netAsset'] ,
                    u'borrowed': open_position['borrowed'] ,
                    u'free': open_position['free'] ,
                    u'interest': open_position['interest'] ,
                    u'locked': open_position['locked'] ,
                    u'has_stop_loss': open_position['has_stop_loss'] ,
                    u'icon': None 
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            logger.debug("👇👇👇👇👇 - set_checked_open_positions successful - 👇👇👇👇👇 ")   
        }    

    # * #######################################################################
    # * Function 
    def set_tradable_assets(self, tradable_list):
            
        db = firestore.Client()
        tradable_assets = db.collection(u'tradable_assets').document()
        now = datetime.now()
        logger.debug("👇👇👇👇👇 - tradable_list - 👇👇👇👇👇 ")        
        logger.debug(tradable_list)
        logger.debug("👆👆👆👆👆 - tradable_list - 👆👆👆👆👆 ")      

        try:
            tradable_assets.set(
                {
                    u'tradable_list': tradable_list,
                    u'time_now': now.strftime("%m/%d/%Y, %H:%M:%S"),
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            print(tradable_assets)
        }

    # * #######################################################################
    # * Function     
    def get_Active_Trades(self):
        print("🚀 RUNNING get_Active_Trades ---------------")
        db = firestore.Client()
        docs = []
        runningTradesData = db.collection(u'active_trades').stream()
        for doc in runningTradesData:
            logger.debug("👇👇👇👇👇 - get_Active_Trades - 👇👇👇👇👇 ")        
            logger.debug(doc)
            logger.debug("👆👆👆👆👆 - get_Active_Trades - 👆👆👆👆👆 ") 
            docs.append(doc.to_dict())
        return docs

    # * #######################################################################
    # * Function     
    def get_open_margin_orders_firebase(self):
        print("🚀 RUNNING get_open_margin_orders ---------------")
        db = firestore.Client()
        docs = []
        open_margin_orders_collection = db.collection(u'open_margin_orders').stream()
        for doc in open_margin_orders_collection:
            open_margin_orders = doc.to_dict()
            open_orders_list = open_margin_orders["open_margin_orders"]
            for open_order in open_orders_list:
                logger.debug("👇👇👇👇👇 - get_open_margin_orders - 👇👇👇👇👇 ")        
                logger.debug(open_order)
                logger.debug("👆👆👆👆👆 - get_open_margin_orders - 👆👆👆👆👆 ") 
                docs.append(open_order)
        return docs

    # * #######################################################################
    # * Function     
    def get_checked_open_positions_firebase(self):
        print("🚀 RUNNING get_checked_open_positions_firebase ---------------")
        db = firestore.Client()
        docs = []
        checked_open_positions_collection = db.collection(u'checked_open_positions').stream()
        for doc in checked_open_positions_collection:            
            logger.debug("👇👇👇👇👇 - checked_open_positions - 👇👇👇👇👇 ")        
            logger.debug(doc.to_dict())
            logger.debug("👆👆👆👆👆 - checked_open_positions - 👆👆👆👆👆 ") 
            docs.append(doc.to_dict())
        return docs

    # * #######################################################################
    # * Function 
    def delete_open_margin_orders(self):
        db = firestore.Client()

        # [START firestore_data_delete_collection]
        def delete_collection(coll_ref, batch_size):
            docs = coll_ref.limit(batch_size).stream()
            deleted = 0

            for doc in docs:
                print(f'Deleting doc {doc.id} => {doc.to_dict()}')
                doc.reference.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return delete_collection(coll_ref, batch_size)
        # [END firestore_data_delete_collection]

        delete_collection(db.collection(u'open_margin_orders'), 10)

    # * #######################################################################
    # * Function     
    def delete_checked_open_positions(self):
        db = firestore.Client()

        # [START firestore_data_delete_collection]
        def delete_collection(coll_ref, batch_size):
            docs = coll_ref.limit(batch_size).stream()
            deleted = 0

            for doc in docs:
                print(f'Deleting doc {doc.id} => {doc.to_dict()}')
                doc.reference.delete()
                deleted = deleted + 1

            if deleted >= batch_size:
                return delete_collection(coll_ref, batch_size)
        # [END firestore_data_delete_collection]

        delete_collection(db.collection(u'checked_open_positions'), 10)

    # * #######################################################################
    # * Function     
    def get_active_trades(self):
        print("🚀 RUNNING get_active_trades ---------------")
        db = firestore.Client()
        docs = []
        active_trades_stream = db.collection(u'active_trades').stream()
        for doc in active_trades_stream:
            logger.debug("👇👇👇👇👇 - get_active_trades - 👇👇👇👇👇 ")        
            logger.debug(doc)
            logger.debug("👆👆👆👆👆 - get_active_trades - 👆👆👆👆👆 ") 
            docs.append(doc.to_dict())
        return docs

    # * #######################################################################
    # * Function 
    def set_active_trade(self, coin_pair, date_open, timeframe, side, stop_loss_pct, account_balance, risk_amount, position_size, entry_price, signal_stop_loss_price, present_price, entry_fee):
            
        db = firestore.Client()
        active_trade_document = db.collection(u'active_trades').document(coin_pair)   

        try:
            active_trade_document.set(
                {
                    u'coin_pair': coin_pair,
                    u'date_open': date_open,
                    u'timeframe': timeframe,
                    u'side': side,
                    u'stop_loss_pct': stop_loss_pct,
                    u'account_balance': account_balance,
                    u'risk_amount': risk_amount,
                    u'position_size': position_size,
                    u'signal_entry_price': entry_price,
                    u'signal_stop_loss_price': signal_stop_loss_price,
                    u'trade_entry_price': present_price,
                    u'entry_fee': entry_fee
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            logger.debug("👇👇👇👇👇 - set_active_trade successful - 👇👇👇👇👇 ")   
        }

    # * #######################################################################
    # * Function prepare_open_margin_orders 
    def get_date_and_fees(self, order_response):
        try:
            #convert from milliseconds, set date and time for each open order
            open_date = int(order_response["transactTime"])
            open_date = datetime.fromtimestamp(open_date/1000)
            open_date = open_date.strftime("%m/%d/%Y, %H:%M:%S")
            side = order_response["side"]
            entry_fee = 0
            present_price = 0
            total_amount = 0
            number_of_fills = 0
            for fill in order_response["fills"]:
                number_of_fills = number_of_fills + 1
                entry_fee = entry_fee + float(fill["commission"])
                total_amount = total_amount + (float(fill["price"])*float(fill["qty"]))
            present_price = round(total_amount/float(order_response["executedQty"]),2)           

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_date, side, entry_fee, present_price

    # * #######################################################################
    # * Function 
    def set_closed_trade(self,exit_order_response):
            
        db = firestore.Client()
        closed_trade_document = db.collection(u'closed_trade').document() 
        active_trades = self.get_active_trades()  
        this_trade = None 
        for active_trade in active_trades:
            if active_trade["coin_pair"] == exit_order_response["symbol"]:
                this_trade = active_trade

        try:
            symbol = exit_order_response["symbol"]
            date_close = exit_order_response["transactTime"]
            position_size = exit_order_response["origQty"]
            trade_exit_price = 0 
            exit_fee = 0 

            date_open = this_trade["date_open"]            
            timeframe = this_trade["timeframe"]
            stop_loss_pct = this_trade["stop_loss_pct"]
            account_balance = this_trade["account_balance"]
            risk_amount = this_trade["risk_amount"]
            signal_entry_price = this_trade["signal_entry_price"]
            signal_stop_loss_price = this_trade["signal_stop_loss_price"]
            trade_entry_price = this_trade["trade_entry_price"] 
            entry_fee = this_trade["entry_fee"]   
                        
            closed_trade_document.set(
                {
                    u'symbol': symbol,
                    u'date_open': date_open,
                    u'date_close': date_close,
                    u'timeframe': timeframe,
                    u'side': "LONG",
                    u'stop_loss_pct': stop_loss_pct,
                    u'account_balance': account_balance,
                    u'risk_amount': risk_amount,
                    u'position_size': position_size,
                    u'signal_entry_price': signal_entry_price,
                    u'signal_stop_loss_price': signal_stop_loss_price,
                    u'trade_entry_price': trade_entry_price,
                    u'trade_exit_price': trade_exit_price,
                    u'entry_fee': entry_fee,
                    u'exit_fee': exit_fee
                }
            )
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
            return False

        return {
            logger.debug("👇👇👇👇👇 - set_closed_trade successful - 👇👇👇👇👇 ")   
        }