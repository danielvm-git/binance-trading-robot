from app import app
from app import config
from app import exchange
from app import database
from app import controller
from app import preparation
import sys
import logging
from flask import request, render_template, jsonify, json

# * ###########################################################################
# * LOGGING INSTANTIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG CLASS INSTANTIATION
# * ###########################################################################
config_client = config.ConfigClient()

# * ###########################################################################
# * EXCHANGE CLASS INSTANTIATION
# * ###########################################################################
exchange_client = exchange.ExchangeClient()

# * ###########################################################################
# * DATABASE CLASS INSTANTIATION
# * ###########################################################################
database_client = database.DatabaseClient()

# * ###########################################################################
# * CONTROLLER CLASS INSTANTIATION
# * ###########################################################################
controller_client = controller.ControllerClient()

# * ###########################################################################
# * PREPARATION CLASS INSTANTIATION
# * ###########################################################################
preparation_client = preparation.PreparationClient()

# * ###########################################################################
# * ROUTE TO HOME
# * ###########################################################################
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def welcome():
    template = controller_client.render_index_page()
    return template

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/openpositions', methods=['GET', 'POST'])                                                                                  
def openpositions():
    checked_open_positions = database_client.get_checked_open_positions_firebase()

    if request.method == 'POST':
        data = []
        for openposition in checked_open_positions:
            asset = openposition["asset"]
            position_value_in_dollar = openposition["position_value_in_dollar"]
            netAsset = openposition["netAsset"]
            borrowed = openposition["borrowed"]
            free = openposition["free"]
            interest = openposition["interest"]
            locked = openposition["locked"]
            has_stop_loss = openposition["has_stop_loss"]
            side = openposition["side"]
            if has_stop_loss == "true":
                has_stop_loss = "<i class=\"far fa-thumbs-up\"></i>"
            else:
                has_stop_loss = "<i class=\"far fa-ban\"></i>"    
            icon = "<i class=\"cf cf-"+asset.lower()+"\"></i>"
            
            data.append({
                'asset': asset ,
                'side': side,
                'position_value_in_dollar': position_value_in_dollar ,
                'netAsset': netAsset ,
                'borrowed': borrowed ,
                'free': free ,
                'interest': interest ,
                'locked': locked ,
                'has_stop_loss': has_stop_loss ,
                'icon': icon 
            })
        
        response = {
            'aaData': data
        }
        return jsonify(response)

# * ###########################################################################
# * ROUTE TO OPEN ORDERS TABLE
# * ###########################################################################
@app.route('/openorders', methods=['GET', 'POST'])                                                                                  
def openorders():    

    if request.method == 'POST': 
        open_margin_orders = database_client.get_open_margin_orders_firebase()
        data = []
        for open_margin_order in open_margin_orders:
            symbol = open_margin_order["symbol"]
            side = open_margin_order["side"]
            quantity = open_margin_order["origQty"]
            stop_price = open_margin_order["stopPrice"]
            update_time = open_margin_order["updateTime"]
            order_id = open_margin_order["orderId"]
            data.append({
                'symbol': symbol ,
                'side': side ,
                'origQty': quantity ,
                'stopPrice': stop_price ,
                'updateTime': update_time ,
                'orderId': order_id
            })
        
        response = {
            'aaData': data
        }
        return jsonify(response)

# * ###########################################################################
# * ROUTE TO WEBHOOK
# * ###########################################################################
@app.route('/webhook', methods=['POST'])
def webhook():
    data = {}
    try:
        data = json.loads(request.data)
    except Exception as e:
        logger.error("an exception occurred - {}".format(e))
        return {"code": "error",
                "message": "Unable to read webhook"}

    if data['password'] != config_client.PASSWORD:
        return {
            "code": "error",
            "message": "Nice try, invalid passphrase"
        }

    interval = data['interval']
    coin_pair = data['ticker']
    signal = data['signal']
    stop_price = 0
    if signal == "ENTRY LONG" or signal == "ENTRY SHORT":
        stop_price = data['stopprice']
        entry_price = data['entryprice']
        usdt_balance = controller_client.get_usdt_balance()
        if signal == "ENTRY LONG":

            sl_percent = round((1 - (stop_price / entry_price)), 4)
            portion_size, risk_amount = preparation_client.portion_size(usdt_balance, sl_percent)
            quantity, coin_rate = controller_client.convert_portion_size_to_quantity(coin_pair, portion_size)
            symbol_info = exchange_client.get_symbol_info(coin_pair)
            rate_steps, quantity_steps = preparation_client.get_tick_and_step_size(symbol_info)
            quantity = preparation_client.rounding_exact_quantity(quantity, quantity_steps)

            trigger_condition = stop_price
            stop_price = stop_price * 0.99
            stop_price = preparation_client.rounding_exact_quantity(stop_price, rate_steps)
            trigger_condition = preparation_client.rounding_exact_quantity(trigger_condition, rate_steps)
            order_response = exchange_client.create_long_order(quantity,coin_pair)
            exchange_client.create_long_stop_loss_order(coin_pair,quantity,stop_price,trigger_condition)
            database_client.set_order(order_response)
            open_date,side,entry_fee,present_price, dollar_size_entry = preparation_client.get_date_and_fees(order_response)
            present_price = preparation_client.rounding_exact_quantity(present_price, rate_steps)
            database_client.set_active_trade(coin_pair,open_date,interval,side,sl_percent,usdt_balance,risk_amount,portion_size,entry_price, stop_price, present_price, entry_fee, rate_steps, quantity_steps, dollar_size_entry)

        elif signal == "ENTRY SHORT":

            sl_percent = round(((stop_price / entry_price) - 1), 4)
            portion_size, risk_amount = preparation_client.portion_size(usdt_balance, sl_percent)
            quantity, coin_rate = controller_client.convert_portion_size_to_quantity(coin_pair, portion_size)
            rate_steps, quantity_steps = preparation_client.get_tick_and_step_size(coin_pair)
            quantity = preparation_client.rounding_exact_quantity(quantity, quantity_steps)

            trigger_condition = stop_price
            stop_price = stop_price * 1.01
            stop_price = preparation_client.rounding_exact_quantity(stop_price, rate_steps)
            trigger_condition = preparation_client.rounding_exact_quantity(trigger_condition, rate_steps)
            order_response = exchange_client.create_short_order(quantity,coin_pair)
            exchange_client.create_short_stop_loss_order(coin_pair,quantity,stop_price,trigger_condition)
            database_client.set_order(order_response)
            open_date,side,entry_fee,present_price = preparation_client.get_date_and_fees(order_response)
            present_price = preparation_client.rounding_exact_quantity(present_price, rate_steps)
            database_client.set_active_trade(coin_pair,open_date,interval,side,sl_percent,usdt_balance,risk_amount,portion_size,entry_price, stop_price, present_price, entry_fee)

    elif signal == "EXIT LONG":
        account_overview = exchange_client.get_margin_account()
        open_orders = exchange_client.get_open_margin_orders()
        quantity, order_id_list = preparation_client.check_is_sl_hit(coin_pair,open_orders,account_overview)
        for order_id in order_id_list:
            exchange_client.cancel_margin_order(coin_pair,order_id)
        order_response = exchange_client.create_exit_long_order(coin_pair,quantity)
        logger.debug("DEBUG")
        logger.debug(order_response)
        logger.debug("DEBUG")
        if order_response != None:
            database_client.set_exit_order(order_response)
            database_client.set_closed_trade(order_response)

    elif signal == "EXIT SHORT":
        account_overview = exchange_client.get_margin_account()
        open_orders = exchange_client.get_open_margin_orders()
        quantity, order_id_list = preparation_client.check_is_sl_hit_short(coin_pair,open_orders,account_overview)
        for order_id in order_id_list:
            exchange_client.cancel_margin_order(coin_pair,order_id)
        order_response = exchange_client.create_exit_short_order(coin_pair,quantity)
        logger.debug("DEBUG")
        logger.debug(order_response)
        logger.debug("DEBUG")
        if order_response != None:
            database_client.set_exit_order(order_response)
            database_client.set_closed_trade(order_response)
    else:
        return "An error occurred, can read the signal"

    if order_response:
        return {
            "code": "success",
            "message": "order executed"
        }
    else:
        logger.error("order failed")

        return {
            "code": "error",
            "message": "order failed"
        }

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/recenttradehistory', methods=['GET', 'POST'])                                                                                  
def recenttradehistory():
    trade_history_list = []
    open_positions = database_client.get_checked_open_positions_firebase()
    for open_position in open_positions:
        symbol = open_position["asset"]
        if symbol != 'USDT' and symbol != 'BNB':
            symbol = symbol + 'USDT'
            tradehistory = exchange_client.get_margin_trades(symbol)
            trade_history_list.append(tradehistory[0])

    return jsonify(trade_history_list)

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/tradehistory', methods=['GET', 'POST'])                                                                                  
def tradehistory():
    trade_history_list = []
    open_positions = database_client.get_checked_open_positions_firebase()
    for open_position in open_positions:
        symbol = open_position["asset"]
        if symbol != 'USDT' and symbol != 'BNB':
            symbol = symbol + 'USDT'
            tradehistory = exchange_client.get_margin_trades(symbol)
            for trade in tradehistory:
                trade_history_list.append(trade)

    return jsonify(trade_history_list)