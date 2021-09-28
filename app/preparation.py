from app import config
import sys
import math
import logging
from datetime import datetime

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
vault = config.ConfigClient()

class PreparationClient:
    # * #######################################################################
    # * Class initialization
    def __init__(self):
        self.base_currency = "BTCUSDT"

    # * #######################################################################
    # * Function prepare_account_overview
    def prepare_account_overview(self,account_overview, margin_price_index):
        try:
            #round margin level
            margin_level = float (account_overview["marginLevel"])
            margin_level = round(margin_level,2)
            position_size = float (account_overview["totalNetAssetOfBtc"])
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
                transact_time = time
                time = datetime.fromtimestamp(time/1000)
                time = self.format_time(time)
                updateTime = int(open_margin_order["updateTime"])
                updateTime = datetime.fromtimestamp(updateTime/1000)
                updateTime = self.format_time(updateTime)
                open_margin_order["time"] = time
                open_margin_order["updateTime"] = updateTime
                open_margin_order["transact_time"] = transact_time
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_margin_orders

    # * #######################################################################
    # * Function format_time 
    def format_time(self, time):
        try:
            time = time.strftime("%m/%d/%Y, %H:%M:%S GMT+0")
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return time

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
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_positions 

    # # * #######################################################################
    # # * Function 
    # def portion_size(self, account_balance, stop_limit_percentage):
    #     risk_amount = account_balance * vault.RISK_FACTOR
    #     portion_size = risk_amount / stop_limit_percentage
    #     return round(portion_size, 2), risk_amount
    def portion_size(self, account_balance, stop_limit_percentage):
        risk_amount = account_balance * vault.RISK_FACTOR
        portion_size = risk_amount / stop_limit_percentage
        return portion_size, risk_amount
    def convert_portion_size_to_quantity(self, coin_price, portion_size):
        try:
            quantity = portion_size / float(coin_price)
            return quantity

        except Exception as e:
            print("an exception occurred - {}".format(e))

    # * #######################################################################
    # * Function 
    def get_tick_and_step_size(self, symbol_info):
        tick_size = None
        step_size = None
        for filter in symbol_info['filters']:
            if filter['filterType'] == 'PRICE_FILTER':
                tick_size = float(filter['tickSize'])
            if filter['filterType'] == 'LOT_SIZE':
                step_size = float(filter['stepSize'])
        return tick_size, step_size

    # * #######################################################################
    # * Function     # Round the quantity or price range, with the actual allowed decimals
    def rounding_exact_quantity(self, quantity, step_size):
        step_size = int(math.log10(1 / float(step_size)))
        quantity = math.floor(float(quantity) * 10 ** step_size) / 10 ** step_size
        quantity = "{:0.0{}f}".format(float(quantity), step_size)
        return str(int(quantity)) if int(step_size) == 0 else quantity
    
    # * #######################################################################
    # * Function 
    def check_is_sl_hit(self, coin_pair, open_orders, account_overview):
        order_id_list = []
        quantity = 0
        asset = coin_pair.replace("USDT","")
        try:
            # TODO test when there is no open order
            open_positions = self.get_open_positions(account_overview)            
            for open_order in  open_orders:
                if open_order["symbol"] == coin_pair:
                    order_id_list.append(open_order["orderId"])                    
            for open_position in open_positions:
                if open_position["asset"] == asset:
                    quantity = quantity + float(open_position["netAsset"])           
        except Exception as e:
                logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return quantity, order_id_list

    # * #######################################################################
    # * Function 
    def check_is_sl_hit_short(self, coin_pair, open_orders, account_overview):
        order_id_list = []
        quantity = 0
        asset = coin_pair.replace("USDT","")
        try:
            open_positions = self.get_open_positions(account_overview)
            
            for open_order in  open_orders:
                if open_order["symbol"] == coin_pair:
                    order_id_list.append(open_order["orderId"])                    
            for open_position in open_positions:
                if open_position["asset"] == asset:
                    quantity = quantity + float(open_position["borrowed"])
        except Exception as e:
                logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return quantity, order_id_list

    # * #######################################################################
    # * Function prepare_open_margin_orders 
    def get_date_and_fees(self, order_response):
        try:
            #convert from milliseconds, set date and time for each open order
            open_date = int(order_response["transactTime"])
            open_date = datetime.fromtimestamp(open_date/1000)
            open_date = self.format_time(open_date)
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
            dollar_size_entry = float(order_response["cummulativeQuoteQty"])     

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return open_date, side, entry_fee, present_price, dollar_size_entry

    # * #######################################################################
    # * Function prepare_open_margin_orders 
    def get_exit_date_and_fees(self, order_response):
        try:
            #convert from milliseconds, set date and time for each open order
            exit_date = int(order_response["transactTime"])
            exit_date = datetime.fromtimestamp(exit_date/1000)
            exit_date = self.format_time(exit_date)
            exit_side = order_response["side"]
            exit_fee = 0
            # exit_price = 0
            total_amount = 0
            number_of_fills = 0
            for fill in order_response["fills"]:
                number_of_fills = number_of_fills + 1
                exit_fee = exit_fee + float(fill["commission"])
                total_amount = total_amount + (float(fill["price"])*float(fill["qty"]))
            # exit_price = round(total_amount/float(order_response["executedQty"]),2)           

        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return exit_date, exit_side, exit_fee

    def get_usdt_balance(self, btc_balance, btc_rate):
        usdt_balance = round(btc_balance * btc_rate, 0)
        return int(usdt_balance)