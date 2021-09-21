from app import config
from app import exchange
from app import database
from app import preparation
from flask import render_template
import sys
import logging

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
# * EXCHANGE CLASS INSTANTIATION
# * ###########################################################################
exchange_client = exchange.ExchangeClient()

# * ###########################################################################
# * DATABASE CLASS INSTANTIATION
# * ###########################################################################
database_client = database.DatabaseClient()

# * ###########################################################################
# * PREPARATION CLASS INSTANTIATION
# * ###########################################################################
preparation_client = preparation.PreparationClient()

# * ###########################################################################
# * Class ControllerClient
class ControllerClient:
    # * #######################################################################
    # * Class initialization
    def __init__(self):
        self.base_currency = "BTCUSDT"
    
    # * #######################################################################
    # * Function get_usdt_balance
    def get_usdt_balance(self):
        try:   
            margin_account = exchange_client.get_margin_account()
            btc_balance = margin_account['totalNetAssetOfBtc']
            btc_balance = float(btc_balance)
            symbol_ticker = exchange_client.get_symbol_ticker(symbol=self.base_currency)
            btc_rate = symbol_ticker['price']
            btc_rate = float(btc_rate)
            usdt_balance = round(btc_balance * btc_rate, 0)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return int(usdt_balance)

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
                margin_price_index = exchange_client.get_margin_price_index(symbol)
                #calculate the position side in US dollar
                position_value_in_dollar = preparation_client.calculate_position_value_in_dollar(margin_price_index,position_size)
                position_value_in_dollar = "${:,.2f}".format(position_value_in_dollar)
                if position_size != 0:
                    open_position["has_stop_loss"] = "false"
                    open_position["side"] = "X"
                    for open_margin_order in open_margin_orders:
                        open_margin_symbol = open_margin_order["symbol"]
                        open_margin_symbol = open_margin_symbol.replace("USDT","")
                        open_position_symbol = open_position["asset"]
                        if open_position_symbol == open_margin_symbol: 
                            open_margin_order_size = float (open_margin_order["origQty"])
                            if open_margin_order["side"] == "SELL":
                                if position_size == open_margin_order_size:
                                    open_position["has_stop_loss"] = "true"
                                    open_position["side"] = "LONG"
                            else:
                                if position_size == -1 * open_margin_order_size:
                                    open_position["has_stop_loss"] = "true"
                                    open_position["side"] = "SHORT"
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
    # * Function 
    def convert_portion_size_to_quantity(self, coin_pair, portion_size):
        try:

            coin_rate = float((exchange_client.get_symbol_ticker(symbol=coin_pair)['price']))
            quantity = portion_size / coin_rate
            return float(quantity), coin_rate

        except Exception as e:
            print("an exception occurred - {}".format(e))

    def render_index_page(self):
        try:
            account_overview = exchange_client.get_margin_account()
            #calculate the position value in dollar
            symbol = "BTCUSDT"
            margin_price_index = exchange_client.get_margin_price_index(symbol)
            #prepare account overview to the frontend
            account_overview_transformed = preparation_client.prepare_account_overview(account_overview,margin_price_index)
            #save account overview to firestore
            database_client.set_account_overview(account_overview_transformed)
            #get open positions from account overview
            open_positions = preparation_client.get_open_positions(account_overview_transformed)
            #get open margin orders from binance
            open_margin_orders = exchange_client.get_open_margin_orders()
            #prepare margin orders for the frontend
            open_margin_orders_transformed = preparation_client.prepare_open_margin_orders(open_margin_orders)
            #save open margin orders to firestore
            database_client.set_open_margin_orders(open_margin_orders_transformed)
            #check if each open order has the proper stop loss
            checked_open_positions = self.has_stop_loss(open_positions,open_margin_orders_transformed)
            #prepare the database to the present list o open positions
            database_client.delete_checked_open_positions()  
            #save each checked open position to the database
            for open_position in checked_open_positions:
                database_client.set_checked_open_position(open_position)
            template = render_template('index.html', account_overview=account_overview_transformed)
        except Exception as e:
            logger.exception("🔥 AN EXCEPTION OCURRED 🔥") 
        return template