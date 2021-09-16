from app import app
from app import exchange
from app import config
import sys
import logging
from flask import Flask, request, render_template, jsonify, json

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
# * ROUTE TO HOME
# * ###########################################################################
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def welcome():
    #get account overview from binance    
    account_overview = exchange_client.get_account_overview()
    #prepare account overview to the frontend
    account_overview_transformed = exchange_client.prepare_account_overview(account_overview)
    #save account overview to firestore
    exchange_client.set_account_overview(account_overview_transformed)
    #get open positions from account overview
    open_positions = exchange_client.get_open_positions(account_overview_transformed)
    #get open margin orders from binance
    open_margin_orders = exchange_client.get_open_margin_orders()
    #prepare margin orders for the frontend
    open_margin_orders_transformed = exchange_client.prepare_open_margin_orders(open_margin_orders)
    #save open margin orders to firestore
    exchange_client.set_open_margin_orders(open_margin_orders_transformed)
    #check if each open order has the proper stop loss
    checked_open_positions = exchange_client.has_stop_loss(open_positions,open_margin_orders_transformed)
    #prepare the database to the present list o open positions
    exchange_client.delete_checked_open_positions()  
    #save each checked open position to the database
    for open_position in checked_open_positions:
        exchange_client.set_checked_open_position(open_position)
    template = render_template('index.html', account_overview=account_overview_transformed)
    return template

# * ###########################################################################
# * ROUTE TO OPEN POSITIONS TABLE
# * ###########################################################################
@app.route('/openpositions', methods=['GET', 'POST'])                                                                                  
def openpositions():
    checked_open_positions = exchange_client.get_checked_open_positions_firebase()

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
            if has_stop_loss == "true":
                has_stop_loss = "<i class=\"far fa-thumbs-up\"></i>"
            else:
                has_stop_loss = "<i class=\"far fa-ban\"></i>"    
            icon = "<i class=\"cf cf-"+asset.lower()+"\"></i>"
            data.append({
                'asset': asset ,
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
        open_margin_orders = exchange_client.get_open_margin_orders_firebase()
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
        usdt_balance = exchange_client.get_usdt_balance()
        if signal == "ENTRY LONG":

            # TODO entry_long - need quantity and symbol
            sl_percent = round((1 - (stop_price / entry_price)), 4)
            portion_size = exchange_client.portion_size(usdt_balance, sl_percent)
            quantity = exchange_client.convert_portion_size_to_quantity(coin_pair, portion_size)
            rate_steps, quantity_steps = exchange_client.get_tick_and_step_size(coin_pair)
            quantity = exchange_client.rounding_exact_quantity(quantity, quantity_steps)

            trigger_condition = stop_price * 1.02
            stop_price = exchange_client.rounding_exact_quantity(stop_price, rate_steps)
            trigger_condition = exchange_client.rounding_exact_quantity(trigger_condition, rate_steps)
            order_response = exchange_client.long_order(quantity,coin_pair)
            exchange_client.set_long_stop_loss(coin_pair,quantity,stop_price,trigger_condition)
            exchange_client.set_order(order_response)

        elif signal == "ENTRY SHORT":

            # TODO entry_short
            sl_percent = round(((stop_price / entry_price) - 1), 4)
            portion_size = exchange_client.portion_size(usdt_balance, sl_percent)
            quantity = exchange_client.convert_portion_size_to_quantity(coin_pair, portion_size)
            rate_steps, quantity_steps = exchange_client.get_tick_and_step_size(coin_pair)
            quantity = exchange_client.rounding_exact_quantity(quantity, quantity_steps)

            trigger_condition = stop_price * 0.98
            stop_price = exchange_client.rounding_exact_quantity(stop_price, rate_steps)
            trigger_condition = exchange_client.rounding_exact_quantity(trigger_condition, rate_steps)
            order_response = exchange_client.long_order(quantity,coin_pair)
            exchange_client.set_short_stop_loss(coin_pair,quantity,stop_price,trigger_condition)
            exchange_client.set_order(order_response)

    elif signal == "EXIT LONG":

        # TODO exit_long
        quantity = exchange_client.check_is_sl_hit(coin_pair)
        order_response = exchange_client.exit_long(coin_pair,quantity)
        logger.debug("DEBUG")
        logger.debug(order_response)
        logger.debug("DEBUG")
        exchange_client.set_stop_loss(order_response)

    elif signal == "EXIT SHORT":
        
        # TODO exit_short
        quantity = exchange_client.check_is_sl_hit(coin_pair)
        order_response = exchange_client.exit_short(coin_pair,quantity)
        logger.debug("DEBUG")
        logger.debug(order_response)
        logger.debug("DEBUG")
        exchange_client.set_stop_loss(order_response)

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