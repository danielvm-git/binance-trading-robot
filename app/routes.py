from app import app
from app import calculate
from app import exchange
from app import config
import sys
import logging
import datetime
from flask import Flask, request, render_template, jsonify, json
from werkzeug.utils import redirect

# * ###########################################################################
# * LOGGING INSTATIATION RETURNING ON CONSOLE
# * ###########################################################################
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logger = logging.getLogger(__name__)

# * ###########################################################################
# * CONFIG CLASS INSTATIATION
# * ###########################################################################
config_client = config.ConfigClient()

# * ###########################################################################
# * CALCULATE CLASS INSTATIATION
# * ###########################################################################
calculate_client = calculate.CalculateClient()

# * ###########################################################################
# * EXCHANGE CLASS INSTATIATION
# * ###########################################################################
exchange_client = exchange.ExchangeClient()

# * ###########################################################################
# * ROUTE TO HOME
# * ###########################################################################
@app.route('/index', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def welcome():    
    account_overview = exchange_client.get_account_overview()
    open_positions = exchange_client.get_open_positions(account_overview)
    open_margin_orders = exchange_client.get_open_margin_orders()
    checked_open_positions = exchange_client.has_stop_loss(open_positions,open_margin_orders)  
    return render_template('index.html', account_overview=account_overview, open_positions=checked_open_positions, open_margin_orders=open_margin_orders)

@app.route('/ajaxfile', methods=['GET', 'POST'])                                                                                  
def ajaxfile():
    account_overview = exchange_client.get_account_overview()
    open_positions = exchange_client.get_open_positions(account_overview)
    open_margin_orders = exchange_client.get_open_margin_orders()
    checked_open_positions = exchange_client.has_stop_loss(open_positions,open_margin_orders) 

    if request.method == 'POST':
        draw = request.form['draw'] 
        row = int(request.form['start'])
        rowperpage = int(request.form['length'])
        searchValue = request.form['search[value]']

        data = []
        totalRecords = len(checked_open_positions)
        for openposition in checked_open_positions:
            teste1 = openposition["asset"]
            teste2 = openposition["position_value_in_dollar"]
            teste3 = openposition["netAsset"]
            teste4 = openposition["borrowed"]
            teste5 = openposition["free"]
            teste6 = openposition["interest"]
            teste7 = openposition["locked"]
            teste8 = openposition["has_stop_loss"]
            if teste8 == "true":
                teste8 = "<i class=\"far fa-thumbs-up\"></i>"
            else:
                teste8 = "<i class=\"far fa-ban\"></i>"    
            teste9 = "<i class=\"cf cf-"+teste1.lower()+"\"></i>"
            data.append({
                'asset': teste1 ,
                'position_value_in_dollar': teste2 ,
                'netAsset': teste3 ,
                'borrowed': teste4 ,
                'free': teste5 ,
                'interest': teste6 ,
                'locked': teste7 ,
                'has_stop_loss': teste8 ,
                'icon': teste9 
            })
        
        response = {
            'draw': draw,
            'iTotalRecords': totalRecords,
            'iTotalDisplayRecords': 20,
            'aaData': data,
        }
        return jsonify(response)

# * ###########################################################################
# * ROUTE TO WEBHOOK TEST
# * ###########################################################################
@app.route('/webhooktest', methods=['POST'])
def webhooktest():
        
    data = {}
    try:
        data = json.loads(request.data)
    except Exception as e:
        logger.error("an exception occured - {}".format(e))
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
        usdt_balance = calculate_client.get_usdt_balance()
        if signal == "ENTRY LONG":

            sl_percent = round((1 - (stop_price / entry_price)), 4)
            portion_size = calculate_client.portion_size(usdt_balance, sl_percent)

            quantity = calculate_client.convert_portion_size_to_quantity(coin_pair, portion_size)
            side = "BUY"
            order_response = calculate_client.long_order(side, quantity, coin_pair, interval, portion_size, stop_price, sl_percent)

        elif signal == "ENTRY SHORT":

            sl_percent = round(((stop_price / entry_price) - 1), 4)
            portion_size = calculate_client.portion_size(usdt_balance, sl_percent)
            quantity = calculate_client.convert_portion_size_to_quantity(coin_pair, portion_size)
            side = "SELL"
            order_response = calculate_client.short_order(side, quantity, coin_pair, interval, portion_size, stop_price, sl_percent)

    elif signal == "EXIT LONG":
        side = "SELL"
        quantity = 0
        portion_size = 0
        order_response = calculate_client.long_order(side, quantity, coin_pair, interval, portion_size, stop_price, sl_percentage=0)


    elif signal == "EXIT SHORT":
        side = "BUY"
        quantity = 0
        portion_size = 0
        order_response = calculate_client.short_order(side, quantity, coin_pair, interval, portion_size, stop_price, sl_percentage=0)
    else:
        return "An error occured, can read the signal"

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
# * ROUTE TO WEBHOOK
# * ###########################################################################
@app.route('/webhook', methods=['POST'])
def webhook():
    data = {}
    try:
        data = json.loads(request.data)
    except Exception as e:
        logger.error("an exception occured - {}".format(e))
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

            # TODO entry_long - preciso quantity e symbol
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
        return "An error occured, can read the signal"

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