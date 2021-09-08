from app import config
import sys
import logging
from datetime import datetime
from google.cloud import secretmanager
from binance.client import Client

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
            symbol = "BTCUSDT"
            margin_price_index = self.get_margin_price_index(symbol)
            position_value_in_dollar = self.calculate_position_value_in_dollar(margin_price_index,position_size)
            account_overview["position_value_in_dollar"] = "${:,.2f}".format(position_value_in_dollar)
            account_overview["tradeEnabled"] = str(account_overview["tradeEnabled"])
            account_overview["transferEnabled"] = str(account_overview["transferEnabled"])
            account_overview["borrowEnabled"] = str(account_overview["borrowEnabled"])
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